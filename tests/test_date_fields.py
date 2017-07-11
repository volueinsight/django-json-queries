import pytest

from django_json_queries.fields import (
    DateField, TimeField, DateTimeField,
    YearField, MonthField, DayField,
    HourField, MinuteField, SecondField,
    WeekField, WeekDayField,
)

from .test_fields import run_test


@pytest.mark.parametrize('input,should_succeed', [
    ('bla', False),
    ('1', False),
    (-1, False),
    (0, False),
    ('2017-01-01', True),
    ('2000-13-01', False),
    ('2000-02-30', False),
])
def test_date_field(input, should_succeed):
    run_test(DateField, input, should_succeed)


@pytest.mark.parametrize('input,should_succeed', [
    ('bla', False),
    ('1', False),
    (-1, False),
    (0, False),
    ('-01:00', False),
    ('00:00', True),
    ('00:00:00', True),
    ('12:00', True),
    ('23:59', True),
    ('23:60', False),
    ('24:00', False),
])
def test_time_field(input, should_succeed):
    run_test(TimeField, input, should_succeed)


@pytest.mark.parametrize('input,should_succeed', [
    ('bla', False),
    ('1', False),
    (-1, False),
    (0, False),
    ('2017-01-01 01:00', False),
    ('2017-01-01T-01:00', False),
    ('2017-02-02T00:00', True),
    ('2017-01-01T00:00:00', True),
    ('2017-01-01T12:00', True),
    ('2017-01-01T23:59', True),
    ('2017-01-01T23:60', False),
    ('2017-01-01T24:00', False),
    ('2017-01-01T00:00Z', True),
    ('2017-01-01T00:00:00Z', True),
    ('2017-01-01T00:00:00+0000', True),
    ('2017-01-01T00:00:00+0200', True),
])
def test_datetime_field(input, should_succeed):
    run_test(DateTimeField, input, should_succeed)


@pytest.mark.parametrize('input,should_succeed', [
    ('bla', False),
    ('1', False),
    (-1, True),
    (0, True),
    (2000, True),
])
def test_year_field(input, should_succeed):
    run_test(YearField, input, should_succeed)


@pytest.mark.parametrize('input,should_succeed', [
    ('bla', False),
    ('1', False),
    (-1, False),
    (0, False),
    (1, True),
    (11, True),
    (12, True),
    (13, False),
])
def test_month_field(input, should_succeed):
    run_test(MonthField, input, should_succeed)


@pytest.mark.parametrize('input,should_succeed', [
    ('bla', False),
    ('1', False),
    (-1, False),
    (0, False),
    (1, True),
    (53, True),
    (54, False),
])
def test_week_field(input, should_succeed):
    run_test(WeekField, input, should_succeed)


@pytest.mark.parametrize('input,should_succeed', [
    ('bla', False),
    ('1', False),
    (-1, False),
    (0, False),
    (1, True),
    (31, True),
    (32, False),
])
def test_day_field(input, should_succeed):
    run_test(DayField, input, should_succeed)


@pytest.mark.parametrize('input,should_succeed', [
    ('bla', False),
    ('1', False),
    (-1, False),
    (0, False),
    (1, True),
    (7, True),
    (8, False),
])
def test_week_day_field(input, should_succeed):
    run_test(WeekDayField, input, should_succeed)


@pytest.mark.parametrize('input,should_succeed', [
    ('bla', False),
    ('1', False),
    (-1, False),
    (0, True),
    (10, True),
    (23, True),
    (24, False),
])
def test_hour_field(input, should_succeed):
    run_test(HourField, input, should_succeed)


@pytest.mark.parametrize('input,should_succeed', [
    ('bla', False),
    ('1', False),
    (-1, False),
    (0, True),
    (30, True),
    (59, True),
    (60, False),
])
def test_minute_field(input, should_succeed):
    run_test(MinuteField, input, should_succeed)


@pytest.mark.parametrize('input,should_succeed', [
    ('bla', False),
    ('1', False),
    (-1, False),
    (0, True),
    (30, True),
    (59, True),
    (60, False),
])
def test_second_field(input, should_succeed):
    run_test(SecondField, input, should_succeed)
