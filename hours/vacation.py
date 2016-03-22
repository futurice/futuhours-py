from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import calendar
import workdays
import copy
from collections import OrderedDict

Holidays = None # TODO: API

def date_to_dt(d):
    if isinstance(d, date):
        d = datetime.combine(d, datetime.min.time())
    return d

def dt_to_date(d):
    if isinstance(d, datetime):
        d = d.date()
    return d

def working_days_total(user, dt, till=False):
    start = dt_to_date(dt)
    last_day_of_month = calendar.monthrange(start.year, start.month)[1]
    if till and (till.month == dt.month and till.year == dt.year):
        last_day_of_month = till.day
    return workdays.networkdays(
        start_date=date(year=start.year, month=start.month, day=start.day),
        end_date=date(year=start.year, month=start.month, day=last_day_of_month),
        holidays=calendar_holidays(user, dt.year))

def working_days(user, dt, till=False):
    start = dt_to_date(dt)
    duration = working_days_total(user, dt, till=till)
    holidays = calendar_holidays(user, dt.year)
    start -= relativedelta(days=1)#include starting day
    days = []
    for k in range(duration):
        start = workdays.workday(start, 1, holidays=holidays)
        days.append(start)
    return days

def user_public_holidays(user, year):
    if not user.account_id:
        return []
    # TODO: Holidays
    holidays = Holidays(user, year).order('day')
    unique_holidays = []
    for holiday in holidays:
        if not any([k.day==holiday.day for k in unique_holidays]):
            unique_holidays.append(holiday)
    return unique_holidays

def calendar_holidays(user, years):
    if not isinstance(years, list):
        years = [years]
    days = []
    for year in years:
        days += [date(year=k.day.year, month=k.day.month, day=k.day.day) for k in \
                user_public_holidays(user, year)]
    return days
