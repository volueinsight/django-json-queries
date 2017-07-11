import pprint
import pytest

from django.db import models

from django_json_queries import Query
from django_json_queries import fields


def test_string_field():
    class CharTestModel(models.Model):
        field = models.CharField()

    class TestQuery(Query):
        class Meta:
            model = CharTestModel
            fields = ['field']

    assert hasattr(TestQuery, 'field'), \
        'field attribute should be set on query'
    assert isinstance(TestQuery.field, fields.StringField), \
        'field instance should be StringField'


def test_integer_field():
    class IntegerTestModel(models.Model):
        field = models.IntegerField()

    class TestQuery(Query):
        class Meta:
            model = IntegerTestModel
            fields = ['field']

    assert hasattr(TestQuery, 'field'), \
        'field attribute should be set on query'
    assert isinstance(TestQuery.field, fields.IntegerField), \
        'field instance should be IntegerField'


def test_float_field():
    class FloatTestModel(models.Model):
        field = models.FloatField()

    class TestQuery(Query):
        class Meta:
            model = FloatTestModel
            fields = ['field']

    assert hasattr(TestQuery, 'field'), \
        'field attribute should be set on query'
    assert isinstance(TestQuery.field, fields.FloatField), \
        'field instance should be FloatField'


def test_boolean_field():
    class BooleanTestModel(models.Model):
        field = models.BooleanField()

    class TestQuery(Query):
        class Meta:
            model = BooleanTestModel
            fields = ['field']

    assert hasattr(TestQuery, 'field'), \
        'field attribute should be set on query'
    assert isinstance(TestQuery.field, fields.BooleanField), \
        'field instance should be BooleanField'


def test_auto_field():
    class AutoTestModel(models.Model):
        field = models.AutoField(primary_key=True)

    class TestQuery(Query):
        class Meta:
            model = AutoTestModel
            fields = ['field']

    assert hasattr(TestQuery, 'field'), \
        'field attribute should be set on query'
    assert isinstance(TestQuery.field, fields.IntegerField), \
        'field instance should be IntegerField'


def test_datetime_field():
    class DateTimeTestModel(models.Model):
        field = models.DateTimeField()

    class TestQuery(Query):
        class Meta:
            model = DateTimeTestModel
            fields = ['field']

    assert hasattr(TestQuery, 'field'), \
        'field attribute should be set on query'
    assert isinstance(TestQuery.field, fields.DateTimeField), \
        'field instance should be DateTimeField'


def test_datetime__year_field():
    class DateTimeYearTestModel(models.Model):
        field = models.DateTimeField()

    class TestQuery(Query):
        class Meta:
            model = DateTimeYearTestModel
            fields = ['field__year']

    assert hasattr(TestQuery, 'field__year'), \
        'field attribute should be set on query'
    assert isinstance(TestQuery.field__year, fields.YearField), \
        'field instance should be YearField'
