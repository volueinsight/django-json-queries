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

ISO8601_TIMESTAMP_RE = re.compile(
    '(?P<year>[+-]?\d{4,})' # Year, must be at least 4 numbers
    # Wither a week date
    '(?P<week>-?W\d{2})'
    '|' # Or a "normal" date
    '('
    '(?P<months>-?\d+M)?'
    '(?P<weeks>-?\d+W)?' # Weeks (not within standard, but accepted by PG)
    '(?P<days>-?\d+D)?'
    '(T' # Start of time
    '(?P<hours>-?\d+H)?' # Hours
    '(?P<minutes>-?\d+M)?' # Minutes
    '(?P<seconds>-?\d+S)?' # Seconds
    ')?' # End of switch between week date and normal date
)


def is_duration(value):
    """
    Check if the given value is a duration (using ISO8601 formatting)

    :param value: The value to check
    :returns: True if the value matches
    """
    return ISO8601_DURATION_RE.fullmatch(value) is not None
