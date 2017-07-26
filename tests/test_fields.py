import pytest

from django.db.models import lookups

from django_json_queries.fields import (
    IntegerField, FloatField, StringField, BooleanField
)


def run_test(field, value, lookup, should_succeed):
    try:
        field.validate(value, lookup)
        if not should_succeed:
            assert False, \
                '"%s" should not be valid for field "%s"' % (value, field)
    except ValueError as e:
        if isinstance(e, AssertionError) or should_succeed:
            raise e


LOOKUPS = {
    'exact': lookups.Exact,
    'in': lookups.In,
}


@pytest.mark.parametrize('input,lookup,should_succeed', [
    ('bla', 'exact', False),
    ('1', 'exact', False),
    (-1, 'exact', True),
    (0, 'exact', True),
    (100, 'exact', True),
    (1321321, 'exact', True),
    (0.12312, 'exact', False),
    (412.321, 'exact', False),
    (True, 'exact', False),
    (False, 'exact', False),
    ([1,2], 'in', True),
    ([1], 'in', True),
    ([1, 1.5], 'in', False),
])
def test_integer_field(input, lookup, should_succeed):
    field = IntegerField(lookups=LOOKUPS)
    run_test(field, input, lookup, should_succeed)


@pytest.mark.parametrize('input,lookup,should_succeed', [
    ('bla', 'exact', False),
    ('1', 'exact', False),
    (-1, 'exact', True),
    (0, 'exact', True),
    (100, 'exact', True),
    (1321321, 'exact', True),
    (0.12312, 'exact', True),
    (412.321, 'exact', True),
    ([1,2], 'in', True),
    ([1, 1.5], 'in', True),
    ([1.0, 1.5], 'in', True),
    (True, 'exact', False),
    (False, 'exact', False),
])
def test_float_field(input, lookup, should_succeed):
    field = FloatField(lookups=LOOKUPS)
    run_test(field, input, lookup, should_succeed)


@pytest.mark.parametrize('input,lookup,should_succeed', [
    ('bla', 'exact', True),
    ('1', 'exact', True),
    ('', 'exact', True),
    ('1\n2\n3', 'exact', True),
    (-1, 'exact', False),
    (0, 'exact', False),
    (0.12312, 'exact', False),
    ([1, 1.5], 'in', False),
    (['a', 'b'], 'in', True),
])
def test_string_field(input, lookup, should_succeed):
    field = StringField(lookups=LOOKUPS)
    run_test(field, input, lookup, should_succeed)


@pytest.mark.parametrize('input,lookup,should_succeed', [
    ('true', 'exact', False),
    ('false', 'exact', False),
    ('True', 'exact', False),
    ('False', 'exact', False),
    (-1, 'exact', False),
    (0, 'exact', False),
    (0.12312, 'exact', False),
    (True, 'exact', True),
    (False, 'exact', True),
    ([True, False], 'in', True),
    ([False], 'in', True),
    ([True], 'in', True),
    ([''], 'in', False),
])
def test_boolean_field(input, lookup, should_succeed):
    field = BooleanField(lookups=LOOKUPS)
    run_test(field, input, lookup, should_succeed)
