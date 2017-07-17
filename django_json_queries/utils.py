"""
This file contains utility methods used to parse and validate input data.

Most of these validations are based on regexes at the moment, but to add
flexibility and improve the accuracy of the validation, the plan is to replace
the more complex validations with actual parsers over time.
"""

import re

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
        return ISO8601_DATE_RE.fullmatch(value) is not None
    else:
        return ISO8601_DATETIME_RE.fullmatch(value) is not None
