import pytest

from django_json_queries.fields import (
    IntegerField, FloatField, StringField, BooleanField
)


def run_test(Field, input, should_succeed):
    field = Field()
    try:
        field.validate(input)
        if not should_succeed:
            assert False, 'Value should not be valid'
    except Exception as e:
        if should_succeed:
            raise e


@pytest.mark.parametrize('input,should_succeed', [
    ('bla', False),
    ('1', False),
    (-1, True),
    (0, True),
    (100, True),
    (1321321, True),
    (0.12312, False),
    (412.321, False),
])
def test_integer_field(input, should_succeed):
    run_test(IntegerField, input, should_succeed)


@pytest.mark.parametrize('input,should_succeed', [
    ('bla', False),
    ('1', False),
    (-1, True),
    (0, True),
    (100, True),
    (1321321, True),
    (0.12312, True),
    (412.321, True),
])
def test_float_field(input, should_succeed):
    run_test(FloatField, input, should_succeed)


@pytest.mark.parametrize('input,should_succeed', [
    ('bla', True),
    ('1', True),
    ('', True),
    ('1\n2\n3', True),
    (-1, False),
    (0, False),
    (0.12312, False),
])
def test_string_field(input, should_succeed):
    run_test(StringField, input, should_succeed)


@pytest.mark.parametrize('input,should_succeed', [
    ('true', False),
    ('false', False),
    ('True', False),
    ('False', False),
    (-1, False),
    (0, False),
    (0.12312, False),
    (True, True),
    (False, True),
])
def test_boolean_field(input, should_succeed):
    run_test(BooleanField, input, should_succeed)
