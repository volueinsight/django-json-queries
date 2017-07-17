import pytest

from django_json_queries import utils


@pytest.mark.parametrize('value,is_valid', [
    ('12', True),
    ('12:00', True),
    ('12:00:00', True),
    ('120000', False),
    ('12 hours', False),
    (1, False),
])
def test_is_time(value, is_valid):
    if is_valid:
        assert utils.is_time(value), \
            '"%s" should be a valid ISO8601 time' % value
    else:
        assert not utils.is_time(value), \
            '"%s" should not be a valid ISO8601 time' % value


@pytest.mark.parametrize('value,is_valid', [
    ('2017', True),
    ('201701', False),     # If only year an month, a dash must be between
    ('2017-0102', False),  # Both month and day should have a separator
    ('2017-01-02', True),
    ('20170102', False),   # Is actually valid, but not accepted at the moment
    ('201701-02', False),  # Both parts must have dashes between
    ('-12-01', False),     # Year is required
    ('2017-W12', True),
    ('2017-W12-1', True),
    ('2017W12', True),
    ('2017W121', True),
    ('201W121', False),    # Year must be as least 4 numbers
    ('201W12', False),     # Year must be as least 4 numbers
    (1, False),            # Should this be valid (year 1)?
])
def test_is_date(value, is_valid):
    if is_valid:
        assert utils.is_date(value), \
            '"%s" should be a valid ISO8601 date' % value
    else:
        assert not utils.is_date(value), \
            '"%s" should not be a valid ISO8601 date' % value


@pytest.mark.parametrize('value,is_valid', [
    ('2017', True),
    ('201701', False),      # If only year an month, a dash must be between
    ('2017-0102', False),   # Both month and day should have a separator
    ('2017-01-02', True),
    ('20170102', False),    # Is actually valid, but not accepted at the moment
    ('201701-02', False),   # Both parts must have dashes between
    ('-12-01', False),      # Year is required
    ('2017-W12', True),
    ('2017-W12-1', True),
    ('2017W12', True),
    ('2017W121', True),
    ('201W121', False),     # Year must be as least 4 numbers
    ('201W12', False),           # Year must be as least 4 numbers
    (1, False),                  # Should this be valid (year 1)?
    ('2017-01-01 00:00', False), # Should have a T as separator
    ('2017-01-01T00:00', True),
])
def test_is_datetime(value, is_valid):
    if is_valid:
        assert utils.is_datetime(value), \
            '"%s" should be a valid ISO8601 datetime' % value
    else:
        assert not utils.is_datetime(value), \
            '"%s" should not be a valid ISO8601 datetime' % value
