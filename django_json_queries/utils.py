"""
This file contains utility methods used to parse and validate input data.

Most of these validations are based on regexes at the moment, but to add
flexibility and improve the accuracy of the validation, the plan is to replace
the more complex validations with actual parsers over time.
"""

import re
import calendar
import datetime
import logging

log = logging.getLogger(__name__)


ISO8601_DURATION_RE = re.compile(
    'P'                     # First char identifying that this is a duration
    '(?P<years>-?\d+Y)?'
    '(?P<months>-?\d+M)?'
    '(?P<weeks>-?\d+W)?'    # Weeks (not within standard, but accepted by PG)
    '(?P<days>-?\d+D)?'
    '(T'                    # Start of time
    '(?P<hours>-?\d+H)?'    # Hours
    '(?P<minutes>-?\d+M)?'  # Minutes
    '(?P<seconds>-?\d+S)?'  # Seconds
    ')?'                    # End of time
)

ISO8601_DATE_RE = re.compile(
    '^'
    '(?P<year>[+-]?\d{4})'
    '('
    '('
    '(-(?P<month>\d{2}))'
    '(-(?P<day>\d{2}))?'
    ')'
    '|'
    '('
    '(-?W(?P<week>\d{2}))'
    '(-?(?P<weekday>\d))?'
    ')'
    ')?'
    '$'
)

ISO8601_TIME_RE = re.compile(
    '^'
    '(?P<hour>\d{2})'
    '(:(?P<minute>\d{2}))?'
    '(:(?P<second>\d{2}(.\d+)?))?'
    '$'
)

ISO8601_DATETIME_RE = re.compile(
    # Year, must be at least 4 numbers and is required for all dates, optionally
    # prefixed with a plus or minus sign.
    '^(?P<year>[+-]?\d{4,})'

    # Date
    '('
    '('
    '-(?P<month>\d{2})'
    '-(?P<day>\d{2})'
    ')'
    '|'
    '('
    '-?W(?P<week>\d{2})'
    '-?(?P<weekday>\d)'
    ')'
    ')'

    # Time
    'T'
    '(?P<hour>\d{2})'
    '(:(?P<minute>\d{2}))?'
    '(:(?P<second>\d{2}(\.\d{1,6})?))?'

    # Time zone info
    '('
    '(?P<zone_utc>Z)'
    '|'
    '('
    '(?P<zone_dir>[+-−])'
    '(?P<zone_hours>\d{2})'
    '(:?(?P<zone_minutes>\d{2}))?'
    ')'
    ')?'
    '$'
)


def is_duration(value):
    """
    Check if the given value is a duration (using ISO8601 formatting)

    :param value: The value to check
    :returns: True if the value matches
    """
    return ISO8601_DURATION_RE.fullmatch(str(value)) is not None


def is_date(value):
    """
    Check if the given value is a valid ISO 8601 formatted date string.

    :param value: The value to check
    :returns: True if the value is a valid date string
    """
    match = ISO8601_DATE_RE.fullmatch(str(value))

    if not match:
        return False

    try:
        _get_date(match.groupdict())
    except:
        log.exception('Invalid date')
        return False

    return True


def is_time(value):
    """
    Check if the given value is a valid ISO 8601 formatted time string.

    :param value: The value to check
    :returns: True if the value is a valid time string
    """
    match = ISO8601_TIME_RE.fullmatch(str(value))

    if not match:
        return False

    try:
        _get_time(match.groupdict())
    except:
        log.exception('Invalid time')
        return False

    return True


def is_datetime(value):
    """
    Check if the given value is a valid ISO 8601 formatted datetime string. This
    will also accept just dates without time and time zone.

    :param value: The value to check
    :returns: True if the value is a valid datetime string
    """
    # We should accept dates as datetimes, so if a 'T' is not present in the
    # input, parse the value as just a date

    value = str(value)
    if 'T' not in value:
        match = ISO8601_DATE_RE.fullmatch(value)
    else:
        match = ISO8601_DATETIME_RE.fullmatch(value)

    # If the string did not match, return false. If it did match, we have to
    # verify the components
    if not match:
        return False

    # Get date from match
    try:
        _get_date(match.groupdict())
    except:
        log.exception('Invalid date')
        return False

    try:
        _get_time(match.groupdict())
    except:
        log.exception('Invalid time')
        return False

    try:
        _get_zone(match.groupdict())
    except:
        log.exception('Invalid time zone')
        return False

    return True


def _weeks_in_year(year):
    # The 28th of December is always in the last week of the year, so this
    # day's weeknumber is the same as the number of weeks in the year
    _, week, _ = datetime.date(year, 12, 28).isocalendar()
    return week


def _week_date(year, week, weekday):
    # The 4th of January is always in the first week of the year, so we can use
    # that as the basis for the calculation.
    date = datetime.date(year, 1, 4)
    date -= datetime.timedelta(days=date.weekday())
    return date + datetime.timedelta(weeks=week - 1, days=weekday - 1)


def _get_from_match(attr, match, default='0'):
    if attr in match and match[attr]:
        return match[attr]
    else:
        return default


def _get_date(match):
    # Year must be in all matches, so this is safe
    year = int(match['year'])
    month = match.get('month', None)
    day = match.get('day', None)
    week = match.get('week', None)
    weekday = match.get('weekday', None)

    if month:
        month = int(month)
        day = int(day) if day else 1
        if month not in range(1, 13):
            raise ValueError('%d is not a valid month' % month)
        _, days_in_month = calendar.monthrange(year, month)
        if day > days_in_month:
            raise ValueError('%d is not a valid day in %d-%d' % (year, month))
        return datetime.date(year, month, day)
    elif week:
        week = int(week)
        weekday = int(weekday) if weekday else 1
        if week not in range(1, _weeks_in_year(year)):
            raise ValueError('%d is not a valid week in year %d' % (week, year))
        if weekday not in range(1, 7):
            raise ValueError('%d is not a valid weekday' % weekday)
        return _week_date(year, week, weekday)
    else:
        return datetime.date(year, 1, 1)


def _get_time(match):
    hour = int(_get_from_match('hour', match))
    minute = int(_get_from_match('minute', match))
    second = _get_from_match('second', match)

    if '.' in second:
        second, fraction = second.split(',', 2)
        fraction = int(fraction.lpad(6, '0'))
    else:
        fraction = 0

    return datetime.time(hour, minute, int(second), fraction)


def _get_zone(match):
    if match.get('zone_utc', None):
        return datetime.timezone.utc

    dir = match.get('zone_dir', None)
    hours = match.get('zone_hours', None)
    minutes = match.get('zone_minutes', None)

    if not dir or not hours:
        return None

    hours = int(hours)
    minutes = int(minutes) if minutes else 0

    if hours not in range(0, 23):
        raise ValueError('%d hours is not a valid time zone offset' % hours)
    if minutes not in range(0, 59):
        raise ValueError('%d minutes is not a valid time zone offset' % minutes)

    if dir == '+':
        return datetime.timezone(datetime.timedelta(hours=hours, minutes=minutes))
    else:
        return datetime.timezone(datetime.timedelta(hours=-hours, minutes=-minutes))
