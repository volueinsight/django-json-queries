import pytest

from django.db.models import lookups

from django_json_queries.fields import (
    DateField, TimeField, DateTimeField,
    YearField, MonthField, DayField,
    HourField, MinuteField, SecondField,
    WeekField, WeekDayField,
)

from .test_fields import run_test


LOOKUPS = {
    'exact': lookups.Exact,
    'in': lookups.In,
}


@pytest.mark.parametrize('input,lookup,should_succeed', [
    ('bla', 'exact', False),
    ('1', 'exact', False),
    (-1, 'exact', False),
    (0, 'exact', False),
    ('2017-01-01', 'exact', True),
    ('2000-13-01', 'exact', False),
    ('2000-02-30', 'exact', False),
    ('P-1Y', 'exact', True),
    ('P-1M', 'exact', True),
    ('P-1D', 'exact', True),
])
def test_date_field(input, lookup, should_succeed):
    field = DateField(lookups=LOOKUPS)
    run_test(field, input, lookup, should_succeed)


@pytest.mark.parametrize('input,lookup,should_succeed', [
    ('bla', 'exact', False),
    ('1', 'exact', False),
    (-1, 'exact', False),
    (0, 'exact', False),
    ('-01:00', 'exact', False),
    ('00:00', 'exact', True),
    ('00:00:00', 'exact', True),
    ('12:00', 'exact', True),
    ('23:59', 'exact', True),
    ('23:60', 'exact', False),
    ('24:00', 'exact', False),
])
def test_time_field(input, lookup, should_succeed):
    field = TimeField(lookups=LOOKUPS)
    run_test(field, input, lookup, should_succeed)


@pytest.mark.parametrize('input,lookup,should_succeed', [
    ('bla', 'exact', False),
    ('1', 'exact', False),
    (-1, 'exact', False),
    (0, 'exact', False),
    ('2017-01-01 01:00', 'exact', False),
    ('2017-01-01T-01:00', 'exact', False),
    ('2017-02-02T00:00', 'exact', True),
    ('2017-01-01T00:00:00', 'exact', True),
    ('2017-01-01T12:00', 'exact', True),
    ('2017-01-01T23:59', 'exact', True),
    ('2017-01-01T23:60', 'exact', False),
    ('2017-01-01T24:00', 'exact', False),
    ('2017-01-01T00:00Z', 'exact', True),
    ('2017-01-01T00:00:00Z', 'exact', True),
    ('2017-01-01T00:00:00+0000', 'exact', True),
    ('2017-01-01T00:00:00+0200', 'exact', True),
    ('P-1Y', 'exact', True),
    ('P-1M', 'exact', True),
    ('P-1D', 'exact', True),
])
def test_datetime_field(input, lookup, should_succeed):
    field = DateTimeField(lookups=LOOKUPS)
    run_test(field, input, lookup, should_succeed)


@pytest.mark.parametrize('input,lookup,should_succeed', [
    ('bla', 'exact', False),
    ('1', 'exact', False),
    (-1, 'exact', True),
    (0, 'exact', True),
    (2000, 'exact', True),
])
def test_year_field(input, lookup, should_succeed):
    field = YearField(lookups=LOOKUPS)
    run_test(field, input, lookup, should_succeed)


@pytest.mark.parametrize('input,lookup,should_succeed', [
    ('bla', 'exact', False),
    ('1', 'exact', False),
    (-1, 'exact', False),
    (0, 'exact', False),
    (1, 'exact', True),
    (11, 'exact', True),
    (12, 'exact', True),
    (13, 'exact', False),
])
def test_month_field(input, lookup, should_succeed):
    field = MonthField(lookups=LOOKUPS)
    run_test(field, input, lookup, should_succeed)


@pytest.mark.parametrize('input,lookup,should_succeed', [
    ('bla', 'exact', False),
    ('1', 'exact', False),
    (-1, 'exact', False),
    (0, 'exact', False),
    (1, 'exact', True),
    (53, 'exact', True),
    (54, 'exact', False),
])
def test_week_field(input, lookup, should_succeed):
    field = WeekField(lookups=LOOKUPS)
    run_test(field, input, lookup, should_succeed)


@pytest.mark.parametrize('input,lookup,should_succeed', [
    ('bla', 'exact', False),
    ('1', 'exact', False),
    (-1, 'exact', False),
    (0, 'exact', False),
    (1, 'exact', True),
    (31, 'exact', True),
    (32, 'exact', False),
])
def test_day_field(input, lookup, should_succeed):
    field = DayField(lookups=LOOKUPS)
    run_test(field, input, lookup, should_succeed)


@pytest.mark.parametrize('input,lookup,should_succeed', [
    ('bla', 'exact', False),
    ('1', 'exact', False),
    (-1, 'exact', False),
    (0, 'exact', False),
    (1, 'exact', True),
    (7, 'exact', True),
    (8, 'exact', False),
])
def test_week_day_field(input, lookup, should_succeed):
    field = WeekDayField(lookups=LOOKUPS)
    run_test(field, input, lookup, should_succeed)


@pytest.mark.parametrize('input,lookup,should_succeed', [
    ('bla', 'exact', False),
    ('1', 'exact', False),
    (-1, 'exact', False),
    (0, 'exact', True),
    (10, 'exact', True),
    (23, 'exact', True),
    (24, 'exact', False),
])
def test_hour_field(input, lookup, should_succeed):
    field = HourField(lookups=LOOKUPS)
    run_test(field, input, lookup, should_succeed)


@pytest.mark.parametrize('input,lookup,should_succeed', [
    ('bla', 'exact', False),
    ('1', 'exact', False),
    (-1, 'exact', False),
    (0, 'exact', True),
    (30, 'exact', True),
    (59, 'exact', True),
    (60, 'exact', False),
])
def test_minute_field(input, lookup, should_succeed):
    field = MinuteField(lookups=LOOKUPS)
    run_test(field, input, lookup, should_succeed)


@pytest.mark.parametrize('input,lookup,should_succeed', [
    ('bla', 'exact', False),
    ('1', 'exact', False),
    (-1, 'exact', False),
    (0, 'exact', True),
    (30, 'exact', True),
    (59, 'exact', True),
    (60, 'exact', False),
])
def test_second_field(input, lookup, should_succeed):
    field = SecondField(lookups=LOOKUPS)
    run_test(field, input, lookup, should_succeed)
