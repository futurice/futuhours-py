from django import forms
from django.shortcuts import render
from django.core.cache import cache
from django.utils import timezone

import hashlib
from collections import OrderedDict
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse as parse_date

from vacation import working_days

Users = None # TODO: API
Hours = None # TODO: API

EMPLOYEE_TYPES = [
'Permanent - full-time',
'Permanent - part-time',
'Subcontractor',
'Permanent - no working time',
'Permanent - hourly pay',
]

TILL = (
('yesterday','Yesterday'),
('today','Today'),
('eom','End of Month'),)

def dtnow():
    return timezone.now()

class BillingForm(forms.Form):
    TYPES = tuple((k,k) for k in EMPLOYEE_TYPES)
    MONTHS = tuple((str(k),str(k)) for k in range(1,4))
    def get_recent_months(self):
        now = datetime.now().replace(day=1)
        dts = []
        for k in range(6):
            dts.append(now)
            now = now - relativedelta(months=1)
        return dts
    def get_recent_months_tuple(self):
        def fmt(dt):
            return '%s-%s'%(dt.month,dt.year)
        return (('','--',),) + tuple((fmt(k),fmt(k),) for k in self.get_recent_months())
    months_total = forms.ChoiceField(choices=MONTHS)
    types = forms.MultipleChoiceField(choices=TYPES)
    till = forms.ChoiceField(choices=TILL)
    only_this_month = forms.ChoiceField(label='Report this month only', choices=(), required=False)
    exclude = forms.CharField(max_length=255, label='Comma separated list of employee usernames to exclude', required=False)

    def __init__(self, *args, **kwargs):
        self.base_fields['only_this_month'].choices = self.get_recent_months_tuple()
        super(BillingForm, self).__init__(*args, **kwargs)

def billing(request):
    duration = 3600
    initial = {
        'months_total': '1',
        'types': ['Permanent - full-time','Permanent - part-time','Permanent - no working time'],
        'till': 'today',
        'exclude': '',
        }
    form = BillingForm(request.POST or None, initial=initial)
    cleaned_data = form.data
    if request.POST:
        form.full_clean()
        cleaned_data = form.cleaned_data
    else:
        cleaned_data = form.initial

    formhash = hashlib.md5(unicode(cleaned_data)).hexdigest()
    key = '{}_{}'.format('billing', formhash)
    key_updated = '{}_updated'.format(key)
    result = cache.get(key)

    if result is None:
        cache.set(key, {}, duration)#poor-man's stampede protection
        only_this_month = cleaned_data.get('only_this_month')
        months = []
        if only_this_month:
            only_this_month = parse_date(only_this_month)
            only_this_month = only_this_month.replace(day=1)
            months = [only_this_month]

        result = find_missing_hour_markings(
                n=int(cleaned_data.get('months_total')),
                wanted_user_types=cleaned_data.get('types'),
                till=cleaned_data.get('till'),
                exclude_usernames=(cleaned_data.get('exclude') or '').split(','),
                only_this_month=only_this_month,
                months=months,
                )
        cache.set(key, result, duration)
        cache.set(key_updated, dtnow(), duration)

    # group hours by year, month
    for tribe, users in result.iteritems():
        for user_index, user in enumerate(users):
            fmt_days = {}
            for day in user[2]:
                fmt_days.setdefault(day.year, {})
                month_human = calendar.month_name[day.month]
                fmt_days[day.year].setdefault(month_human, [])
                fmt_days[day.year][month_human].append(day)
            result[tribe][user_index][2] = fmt_days

    updated = cache.get(key_updated) or dtnow()
    context = {
        'updated': int((dtnow()-updated).total_seconds()/60),
        'result': result,
        'update_interval': int(duration/60),
        'form': form,
    }
    return render(request, 'billing.html', context)

def find_missing_hour_markings(till, n=1, wanted_user_types=None, exclude_usernames=[], months=[], only_this_month=None):
    teams = OrderedDict()
    teams[''] = OrderedDict({'name': 'No Tribe', 'users': []})
    now = datetime.now().replace(day=1)

    def till_end_of_month(dt):
        last_day_of_month = calendar.monthrange(dt.year, dt.month)[1]
        return dt.replace(day=last_day_of_month)

    if till:
        if till == 'yesterday':
            till = (datetime.now() - relativedelta(days=1))
        if till == 'today':
            till = datetime.now()
        if till == 'eom':
            dt_cmp = datetime.now() if not only_this_month else only_this_month
            till = till_end_of_month(dt_cmp)
    else:
        till = (datetime.now() - relativedelta(days=1))

    if not months:
        months.append(now)
        st = now
        for k in range(1, n):
            st -= relativedelta(months=1)
            months.append(st)

    #for user in Users.objects.filter(active=True).order_by('username'):
    for user in []:
        if wanted_user_types and user.type not in wanted_user_types:
            continue
        if user.username in exclude_usernames:
            continue
        team = user.primary_team or ''
        total_missing_days = []
        if team and not teams.get(team):
            teams.setdefault(team, OrderedDict())
            teams[team].setdefault('name', team.name)
            teams[team].setdefault('users', [])
        for start in months:
            if only_this_month:
                if (start.month != only_this_month.month and start.year != only_this_month.year):
                    continue
                else:
                    end = till = till_end_of_month(start)
            else:
                if start.month == till.month and start.year == till.year:
                    end = till + relativedelta(days=1)
                else:
                    end = start + relativedelta(months=1)
            hours = Hours.objects.filter(user=user, day__gte=start, day__lte=end)
            hour_markings = [k.day for k in hours]
            missing_days = set(working_days(user, start, till=till)).difference(set(hour_markings))
            if missing_days:
                total_missing_days += missing_days
        formatted_missing_days = sorted(total_missing_days)
        teams[team]['users'].append([user, user.balance, formatted_missing_days])
    g = OrderedDict()
    for k in teams.keys():
        g.setdefault(teams[k]['name'], [])
        g[teams[k]['name']] = teams[k]['users']
    return g
