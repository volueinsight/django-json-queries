"""
This file contains utility methods used to parse and validate input data.

Most of these validations are based on regexes at the moment, but to add
flexibility and improve the accuracy of the validation, the plan is to replace
the more complex validations with actual parsers over time.
"""

import re
import calendar
import datetime


ISO8601_DURATION_RE = re.compile(
    'P' # First char identifying that this is a duration
    '(?P<years>-?\d+Y)?'
    '(?P<months>-?\d+M)?'
    '(?P<weeks>-?\d+W)?' # Weeks (not within standard, but accepted by PG)
    '(?P<days>-?\d+D)?'
    '(T' # Start of time
    '(?P<hours>-?\d+H)?' # Hours
    '(?P<minutes>-?\d+M)?' # Minutes
    '(?P<seconds>-?\d+S)?' # Seconds
    ')?' # End of time
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
    '(:(?P<second>\d{2}(.\d+)?))?'

    # Time zone info
    '(Z)?'
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
    return ISO8601_DATE_RE.fullmatch(str(value)) is not None


def is_time(value):
    """
    Check if the given value is a valid ISO 8601 formatted time string.

    :param value: The value to check
    :returns: True if the value is a valid time string
    """
    return ISO8601_TIME_RE.fullmatch(str(value)) is not None


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
        date = _get_date(match)
    except:
        return False

    return True


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
        return date(year, month, day)
    elif week:
        week = int(week)
        weekday = int(weekday) if weekday else 1
    else:
        return date(year, 1, 1)


def _get_time(match):
    hour = int(match.get('hour', '0'))
    minute = int(match.get('minute', '0'))
    second = match.get('second', '0')

    if '.' in second:
        second, fraction = second.split(',', 2)
