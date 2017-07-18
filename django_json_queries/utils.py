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

from django.core.exceptions import ValidationError

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
    '(?P<year>\d{4})'
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
    '(:(?P<second>\d{2}(\.\d{1,6})?))?'
    '$'
)

ISO8601_DATETIME_RE = re.compile(
    '^'
    '(?P<year>\d{4})'

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
    '[Tt]'
    '(?P<hour>\d{2})'
    '(:(?P<minute>\d{2}))?'
    '(:(?P<second>\d{2}(\.\d{1,6})?))?'

    # Time zone info
    '('
    '(?P<zone_utc>[Zz])'
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
    try:
        parse_date(value)
        return True
    except ValidationError:
        log.exception('Invalid date')
        return False


def parse_date(value):
    match = ISO8601_DATE_RE.fullmatch(str(value))

    if not match:
        raise ValidationError(
            '"%(value)s" is not a valid ISO8601 date.',
            params={'value': value},
            code='invalid',
        )

    return _get_date(match.groupdict())



def is_time(value):
    """
    Check if the given value is a valid ISO 8601 formatted time string.

    :param value: The value to check
    :returns: True if the value is a valid time string
    """
    try:
        parse_time(value)
        return True
    except ValidationError:
        log.exception('Invalid time')
        return False

def parse_time(value):
    match = ISO8601_TIME_RE.fullmatch(str(value))

    if not match:
        raise ValidationError(
            '"%(value)s" is not a valid ISO8601 time.',
            params={'value': value},
            code='invalid',
        )

    return _get_time(match.groupdict())


def is_datetime(value):
    """
    Check if the given value is a valid ISO 8601 formatted datetime string. This
    will also accept just dates without time and time zone.

    :param value: The value to check
    :returns: True if the value is a valid datetime string
    """
    try:
        parse_datetime(value)
        return True
    except ValidationError:
        log.exception('Invalid date or datetime')
        return False

def parse_datetime(value):
    """
    Parse the value into a python datetime object. The specified value must be
    a valid ISO8601 date or datetime formatted string.

    A ValidationError is raised if the given value does not match the expected
    format or is an invalid date.

    :param value: The value to parse into a datetime
    :returns: A datetime object
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
        raise ValidationError(
            '"%(value)s" is not a valid ISO8601 date or datetime.',
            params={'value': value},
            code='invalid',
        )

    # Get components from the regex match
    date = _get_date(match.groupdict())
    time = _get_time(match.groupdict())
    zone = _get_zone(match.groupdict())

    # Return datetime object
    return datetime.datetime.combine(date, time).replace(tzinfo=zone)


def _weeks_in_year(year):
    # The 28th of December is always in the last week of the year, so this
    # day's weeknumber is the same as the number of weeks in the year
    _, week, _ = datetime.date(year, 12, 28).isocalendar()
    return week


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
        return _get_calendar_date(year, month, day)
    elif week:
        return _get_week_date(year, week, weekday)
    else:
        return datetime.date(year, 1, 1)


def _get_calendar_date(year, month, day):
    month = int(month)
    day = int(day) if day else 1
    if month not in range(1, 13):
        raise ValidationError(
            '%(value)d is not a valid month, '
            'please specify a month between 1 and 12.',
            params={'value': month},
            code='invalid',
        )
    _, days_in_month = calendar.monthrange(year, month)
    if day > days_in_month:
        raise ValidationError(
            '%(value)d is not a valid day in %(month_name)s %(year)d, '
            'please specify a day between 1 and %(days_in_month)d.',
            params={
                'value': day,
                'month_name': calendar.month_name[month],
                'year': year,
                'days_in_month': days_in_month,
            },
            code='invalid',
        )
    return datetime.date(year, month, day)


def _get_week_date(year, week, weekday):
    week = int(week)
    weekday = int(weekday) if weekday else 1
    weeks_in_year = _weeks_in_year(year)
    if week not in range(1, weeks_in_year+1):
        raise ValidationError(
            '%(value)d is not a valid week in year %(year)d.',
            params={'value': week, 'year': year},
            code='invalid',
        )
    if weekday not in range(1, 8):
        raise ValidationError(
            '%(value)d is not a valid weekday, '
            'please specify a day between 1 and 7.',
            params={'value': weekday},
            code='invalid',
        )

    # The 4th of January is always in the first week of the year, so we can use
    # that as the basis for the calculation.
    date = datetime.date(year, 1, 4)
    date -= datetime.timedelta(days=date.weekday())
    return date + datetime.timedelta(weeks=week - 1, days=weekday - 1)


def _get_time(match):
    hour = int(_get_from_match('hour', match))
    minute = int(_get_from_match('minute', match))
    second = _get_from_match('second', match)

    # Check for and handle a seconds fraction
    if '.' in second:
        second, fraction = second.split('.', 2)
        fraction = int(fraction.ljust(6, '0'))
    else:
        fraction = 0
    second = int(second)

    # Validate that all components are within their valid ranges
    if hour not in range(0, 24):
        raise ValidationError(
            '%(value)d is not a valid hour, '
            'please enter an hour between 0 and 23',
            params={'value': hour},
            code='invalid',
        )
    if minute not in range(0, 60):
        raise ValidationError(
            '%(value)d is not a valid minute, '
            'please enter a minute between 0 and 59',
            params={'value': minute},
            code='invalid',
        )
    if second not in range(0, 60):
        raise ValidationError(
            '%(value)d is not a valid second, '
            'please enter a second between 0 and 59',
            params={'value': second},
            code='invalid',
        )

    return datetime.time(hour, minute, second, fraction)


def _get_zone(match):
    """
    Helper function to get a timezone object from the specified match, if
    specified. If no time zone info is specified, None is returned. If invalid
    time zone info is specified, an exception will be raised.
    """
    if match.get('zone_utc', None):
        return datetime.timezone.utc

    dir = match.get('zone_dir', None)
    hours = match.get('zone_hours', None)
    minutes = match.get('zone_minutes', None)

    if not dir or not hours:
        return None

    hours = int(hours)
    minutes = int(minutes) if minutes else 0

    if hours not in range(0, 24):
        raise ValidationError(
            '%(value)d hours is not a valid time zone offset',
            params={'value': hours},
            code='invalid',
        )
    if minutes not in range(0, 60):
        raise ValidationError(
            '%(value)d minutes is not a valid time zone offset',
            params={'value': minutes},
            code='invalid',
        )

    if dir == '+':
        return datetime.timezone(datetime.timedelta(hours=hours, minutes=minutes))
    else:
        return datetime.timezone(datetime.timedelta(hours=-hours, minutes=-minutes))
