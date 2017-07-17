from collections import Iterable

from datetime import date, time, datetime

from django.db.models.functions import Now
from django.utils.dateparse import parse_date, parse_time, parse_datetime

from .utils import is_duration, is_datetime, is_date, is_time


__all__ = [
    'IntegerField', 'FloatField', 'StringField', 'BooleanField',
    'DateField', 'TimeField', 'DateTimeField',
    'YearField', 'MonthField', 'WeekField', 'DayField', 'WeekDayField',
    'HourField', 'MinuteField', 'SecondField',
]


class FieldBase(type):
    def __new__(cls, name, bases, attrs):
        super_new = super().__new__

        # Make sure input_type is iterable
        if 'input_type' in attrs and not isinstance(attrs['input_type'], Iterable):
            attrs['input_type'] = (attrs['input_type'], )

        # TODO: Perform some kind of validation probably
        return super_new(cls, name, bases, attrs)


class Field(metaclass=FieldBase):
    """Base class for all fields types"""

    def __init__(self, verbose_name=None, name=None, model_name=None,
                 lookups=None):
        # Perform some basic validation
        assert isinstance(lookups, dict), \
            'Lookups must be a dict with name and lookup classes'

        self.verbose_name = verbose_name
        self.model_name = model_name
        self.name = name
        self.lookups = lookups

    def __repr__(self):
        """Display the module, class, and name of the field."""
        cls = self.__class__
        path = '%s.%s' % (cls.__module__, cls.__qualname__)
        name = getattr(self, 'name', None)
        if name is not None:
            return '<%s: %s>' % (path, name)
        return '<%s>' % path

    @classmethod
    def desc(cls):
        """
        Return a field description for this field. This includes the field name,
        verbose name, expected input type (string, int, etc.) and the value type
        (e.g. date/datetime etc). The response from this method is meant as a
        way to generate user interfaces.

        :returns: A dict describing this field
        """
        return dict(
            name=self.name,
            verbose_name=self.verbose_name,
            input_type=self.input_type.__name__,
            value_type=self.value_type,
        )

    def validate(self, value, lookup):
        """
        Basic field validation. This method checks that the input type is of the
        specified class for this field. Subclasses should override this method
        and provide better validation.

        :param value: The value to validate
        """
        if not lookup in self.lookups:
            raise ValueError('Unsupported lookup: %s' % lookup)

        if hasattr(self, 'validate_%s' % lookup):
            func = getattr(self, 'validate_%s' % lookup)
            func(value, lookup)
        else:
            self._check_type(value)

    def validate_in(self, value, lookup):
        if not isinstance(value, list):
            raise ValueError('Value must be a list')

        for i, item in enumerate(value):
            self._check_type(item)

    def _check_type(self, value):
        if not isinstance(value, self.input_type):
            raise ValueError('Please provide a valid value')
        if int in self.input_type:
            if isinstance(value, bool):
                raise ValueError('Please provide a valid value')

    def prepare(self, value, lookup):
        """
        Prepare the specified value for querying. The lookup is also provided in
        case value parsing is dependent on the lookup type.

        :param value: The raw value being queried
        :param lookup: The current lookup.
        """
        return value

    #
    # The methods below are "private" methods not generally used
    #

    def set_attributes_from_name(self, name):
        if not self.name:
            self.name = name

        if not self.model_name:
            self.model_name = name

        if self.verbose_name is None and self.name:
            self.verbose_name = self.name.replace('_', ' ')

    def contribute_to_class(self, cls, name):
        """
        Register this field on the class, with a name set

        :param cls: The class to register the field on
        :param name: The attribute name on the class
        """

        self.set_attributes_from_name(name)
        self.query = cls

        # Register the field on the class
        # TODO: Register field with cls._meta instead
        setattr(cls, name, self)


class RangeFieldBase(FieldBase):
    def __new__(cls, name, bases, attrs):
        super_new = super().__new__

        # Ensure initialization is only performed for subclasses of RangeField
        # (excluding the RangeField class itself). For anything else, we fall
        # back to the default type.__new__ method instead of going through the
        # FieldBase metaclass initialization.
        parents = [b for b in bases if isinstance(b, RangeFieldBase)]
        if not parents:
            return type.__new__(cls, name, bases, attrs)

        # Validate that a range of values have been specified
        if 'value_range' not in attrs:
            raise RuntimeError(
                'Range field %s.%s does not define a range' % (
                    attrs['__module__'], name
                )
            )

        # Initialize class
        return super().__new__(cls, name, bases, attrs)


class RangeField(Field, metaclass=RangeFieldBase):
    def validate(self, value, lookup):
        super().validate(value, lookup)

        # Validate the the value is within the allowed range
        if not value in self.value_range:
            raise ValueError('Value %s is not within range %s' % (
                value, self.value_range
            ))


class ChoiceFieldBase(FieldBase):
    def __new__(cls, name, bases, attrs):
        super_new = super().__new__

        # Ensure initialization is only performed for subclasses of ChoiceField
        # (excluding the ChoiceField class itself). For anything else, we fall
        # back to the default type.__new__ method instead of going through the
        # FieldBase metaclass initialization.
        parents = [b for b in bases if isinstance(b, ChoiceFieldBase)]
        if not parents:
            return type.__new__(cls, name, bases, attrs)

        # Initialize class
        new_class = super().__new__(cls, name, bases, attrs)

        choices = attrs.get('choices', None)
        if not choices:
            raise RuntimeError(
                'Choice field %s.%s does not define any choices' % (
                    attrs['__module__'], name
                )
            )

        # Extract the keys from the specified choices and set is as an attribute
        # on the newly created class.
        setattr(new_class, 'keys', [c[0] for c in choices])

        return new_class


class ChoiceField(Field, metaclass=ChoiceFieldBase):

    @classmethod
    def desc(cls):
        """
        Return a field description for this field. This includes the field name,
        verbose name, expected input type (string, int, etc.) and the value type
        (e.g. date/datetime etc). The response from this method is meant as a
        way to generate user interfaces.

        :returns: A dict describing this field
        """
        desc = super().desc()
        desc['choices'] = cls.choices
        return desc

    def validate(self, value, lookup):
        super().validate(value, lookup)

        # Validate that the given value is one of the allowed ones
        if not value in self.keys:
            raise ValueError('Please provide a valid value')


class IntegerField(Field):
    value_type = 'int'
    input_type = int


class FloatField(Field):
    value_type = 'float'
    input_type = (int, float)


class StringField(Field):
    value_type = 'string'
    input_type = str


class BooleanField(Field):
    value_type = 'boolean'
    input_type = bool


class DateField(Field):
    value_type = 'date'
    input_type = str

    def validate(self, value, lookup):
        # Let super validate the value type
        super().validate(value, lookup)

        # Check if a duration was provided
        if is_duration(value) or is_date(value):
            return

        raise ValueError('Please provide a valid date or duration')

    def prepare(self, value, lookup):
        """
        Prepare the specified value as either a relative date or a date object.

        :param value: The raw value being queried
        :param lookup: The current lookup.
        """

        if is_duration(value):
            return Now() + value
        else:
            return parse_date(value)


class TimeField(Field):
    value_type = 'time'
    input_type = str

    def validate(self, value, lookup):
        # Let super validate the value type
        super().validate(value, lookup)

        # Try to parse as a time
        if not parse_time(value):
            raise ValueError('Please provide a valid time')


class DateTimeField(Field):
    value_type = 'datetime'
    input_type = str

    def validate(self, value, lookup):
        # Let super validate the value type
        super().validate(value, lookup)

        # Check if a duration was provided
        if is_duration(value) or is_datetime(value):
            return

        raise ValueError('Please provide a valid datetime')

    def prepare(self, value, lookup):
        """
        Prepare the specified value as either a relative datetime or a date
        object.

        :param value: The raw value being queried
        :param lookup: The current lookup.
        """

        if is_duration(value):
            return Now() + value
        else:
            return parse_datetime(value)


class YearField(Field):
    value_type = 'year'
    input_type = int


class MonthField(ChoiceField):
    value_type = 'month'
    input_type = int
    choices = [
        ( 1, 'January'),
        ( 2, 'February'),
        ( 3, 'March'),
        ( 4, 'April'),
        ( 5, 'May'),
        ( 6, 'June'),
        ( 7, 'July'),
        ( 8, 'August'),
        ( 9, 'September'),
        (10, 'October'),
        (11, 'November'),
        (12, 'December'),
    ]


class WeekDayField(ChoiceField):
    value_type = 'week_day'
    input_type = int
    choices = [
        (2, 'Monday'),
        (3, 'Tuesday'),
        (4, 'Wednesday'),
        (5, 'Thursday'),
        (6, 'Friday'),
        (7, 'Saturday'),
        (1, 'Sunday'),
    ]


class WeekField(RangeField):
    value_type = 'week'
    value_range = range(1, 54)
    input_type = int


class DayField(RangeField):
    value_type = 'day'
    value_range = range(1, 32)
    input_type = int


class HourField(RangeField):
    value_type = 'hour'
    value_range = range(0, 24)
    input_type = int


class MinuteField(RangeField):
    value_type = 'minute'
    value_range = range(0, 60)
    input_type = int


class SecondField(RangeField):
    value_type = 'second'
    value_range = range(0, 60)
    input_type = int
