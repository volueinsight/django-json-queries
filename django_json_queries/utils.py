import re

ISO8601_DURATION_RE = re.compile(
    'P' # First char identifying that this is a duration
    '(-?\d+Y)?' # Year
    '(-?\d+M)?' # Month
    '(-?\d+W)?' # Week (not within standard, but accepted by PG)
    '(-?\d+D)?' # Month
    '(T' # Start of time
    '(-?\d+H)?' # Year
    '(-?\d+M)?' # Month
    '(-?\d+S)?' # Month
    ')?' # End of time
)

def is_duration(value):
    """
    Check if the given value is a duration (using ISO8601 formatting)

    :param value: The value to check
    :returns: True if the value matches
    """
    return ISO8601_DURATION_RE.fullmatch(value) is not None
