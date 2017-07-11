import pytest

from django_json_queries.fields import (
    IntegerField, FloatField, StringField, BooleanField
)


def run_test(Field, input, lookup, should_succeed):
    field = Field()
    try:
        field.validate(input, lookup)
        if not should_succeed:
            assert False, 'Value should not be valid'
    except Exception as e:
        if should_succeed:
            raise e


@pytest.mark.parametrize('input,lookup,should_succeed', [
    ('bla', 'exact', False),
    ('1', 'exact', False),
    (-1, 'exact', True),
    (0, 'exact', True),
    (100, 'exact', True),
    (1321321, 'exact', True),
    (0.12312, 'exact', False),
    (412.321, 'exact', False),
])
def test_integer_field(input, lookup, should_succeed):
    run_test(IntegerField, input, lookup, should_succeed)


@pytest.mark.parametrize('input,lookup,should_succeed', [
    ('bla', 'exact', False),
    ('1', 'exact', False),
    (-1, 'exact', True),
    (0, 'exact', True),
    (100, 'exact', True),
    (1321321, 'exact', True),
    (0.12312, 'exact', True),
    (412.321, 'exact', True),
])
def test_float_field(input, lookup, should_succeed):
    run_test(FloatField, input, lookup, should_succeed)


@pytest.mark.parametrize('input,lookup,should_succeed', [
    ('bla', 'exact', True),
    ('1', 'exact', True),
    ('', 'exact', True),
    ('1\n2\n3', 'exact', True),
    (-1, 'exact', False),
    (0, 'exact', False),
    (0.12312, 'exact', False),
])
def test_string_field(input, lookup, should_succeed):
    run_test(StringField, input, lookup, should_succeed)


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
])
def test_boolean_field(input, lookup, should_succeed):
    run_test(BooleanField, input, lookup, should_succeed)
