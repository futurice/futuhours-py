import copy
from datetime import datetime, timedelta, date
from collections import OrderedDict

import workdays

Vacations = None # TODO: API

def user_vacations(user):
    return Vacations(user=user, remaining__gt=0).order_by('year')

def vacation_days(user, start, end):
    """ Calculate used working days for the duration of vacation """
    start, end = dt_to_date(start), dt_to_date(end)
    duration = vacation_duration(user, start, end)
    years = list(set([start.year, end.year]))
    holidays = calendar_holidays(user, years)
    days = []
    start -= relativedelta(days=1)#include starting day
    for k in range(duration):
        start = workdays.workday(start, 1, holidays=holidays)
        days.append(start)
    return days

def vacation_duration(user, start, end, accounting=False):
    """ Calculate duration of vacation in number of days
    accounting: for calculating days total based on Finnish law
    """
    start, end = dt_to_date(start), dt_to_date(end)
    years = list(set([start.year, end.year]))
    duration = workdays.networkdays(
        start_date=date(year=start.year, month=start.month, day=start.day),
        end_date=date(year=end.year, month=end.month, day=end.day),
        holidays=calendar_holidays(user, years))
    if accounting:
        # for Finnish accounts: every full week, a sixth vacation day is used
        if user.account_id and user.account.country==u'Finland':
            duration += int(duration/5)
    return duration

def apply_vacation(user, start, end):
    """
    Generate arguments for PlanMill API to apply an Annual Holiday absence.

    A)
    5 vacation days 2014
    vacation duration: 5 days
     - single entry
    B)
    1 vacation day from 2013
    4 vacation days from 2014
    vacation duration: 5 days
     - two entries: one 1 day, one 4 day
    """
    start, end = dt_to_date(start), dt_to_date(end)
    years = list(set([start.year, end.year]))
    duration = vacation_duration(user, start, end)
    vacations = user_vacations(user)
    calls = split_logic(user, start, end, duration, vacations)
    return calls

def get_slots(duration, vacations):
    days = OrderedDict()
    for vacation in vacations:
        key = vacation.year
        days.setdefault(key, 0)
        while sum(days.values())<duration and vacation.remaining>0:
            vacation.remaining -= 1
            days[key] += 1
    return days

def split_logic(user, start, end, duration, vacations):
    calls = []
    slots = get_slots(duration, vacations)
    years = list(set([start.year, end.year]))
    holidays = calendar_holidays(user, years)
    end_holiday = copy.deepcopy(end)
    for year,days in slots.iteritems():
        days = days-1#to include starting day; eg. days=1 skips to next day, days=0 includes starting day
        end = workdays.workday(start, days, holidays=holidays)
        c = {
            'extra_params': {
                'Task.VacationYear': year,},
            'start': copy.deepcopy(start),
            'end': copy.deepcopy(end),
        }
        start = workdays.workday(start, days+1, holidays=holidays)
        calls.append(c)
        # There can be more slots than the length of the vacation; short circuit
        if end>=end_holiday:
            break
    return calls
