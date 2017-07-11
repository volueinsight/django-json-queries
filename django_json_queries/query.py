import inspect

from django.db import models
from django.db.models import functions
from django.db.models.constants import LOOKUP_SEP
from django.db.models.expressions import Expression
from django.db.models.lookups import Transform

from . import fields
from . import conditions


def _get_output_field(field, transform_name, query):
    expr = Expression(field)
    # TODO: Third argument removed in Django 2.0
    result = query.try_transform(expr, transform_name, None)
    return result.output_field


# Default mappings from model field to our query fields.
FIELD_FOR_DBFIELD_DEFAULTS = {
    models.DateField:           {'field_class': fields.DateField},
    models.DateTimeField:       {'field_class': fields.DateTimeField},
    models.TimeField:           {'field_class': fields.TimeField},
    models.AutoField:           {'field_class': fields.IntegerField},
    models.IntegerField:        {'field_class': fields.IntegerField},
    models.FloatField:          {'field_class': fields.FloatField},
    models.CharField:           {'field_class': fields.StringField},
    models.TextField:           {'field_class': fields.StringField},
    models.BooleanField:        {'field_class': fields.BooleanField},
}

# Default mappings from database functions to our query fields
FIELD_FOR_DBFUNCTION_DEFAULTS = {
    functions.ExtractYear:      {'field_class': fields.YearField},
    functions.ExtractMonth:     {'field_class': fields.MonthField},
    functions.ExtractDay:       {'field_class': fields.DayField},
    functions.ExtractHour:      {'field_class': fields.HourField},
    functions.ExtractMinute:    {'field_class': fields.MinuteField},
    functions.ExtractSecond:    {'field_class': fields.SecondField},
    functions.ExtractWeekDay:   {'field_class': fields.WeekDayField},
    functions.ExtractWeek:      {'field_class': fields.WeekField},
}


class QueryBase(type):
    """
    Metaclass for queries. This validates that the required attributes are
    specified to avoid random errors later.
    """

    def __new__(cls, name, bases, attrs):
        super_new = super().__new__

        # Ensure initialization is only performed for subclasses of Query
        # (excluding the Query class itself).
        parents = [b for b in bases if isinstance(b, QueryBase)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        # Initialize the new class
        new_class = super_new(cls, name, bases, {
            '__module__': attrs.pop('__module__'),
        })

        # Get meta class
        meta = attrs.get('Meta', None)
        if not meta:
            # TODO: Make optional
            raise RuntimeError(
                'Query %s.%s does not define a meta class' % (
                    attrs['__module__'], name
                )
            )

        # TODO: Make OptionsClass like Django
        setattr(new_class, '_meta', meta)

        # Make sure conditions are set, or set to the default
        _conditions = getattr(meta, 'conditions', {
            'and': conditions.AndCondition,
            'or': conditions.OrCondition,
            'lookup': conditions.LookupCondition,
        })
        setattr(meta, 'conditions', _conditions)

        # Check that a model has been specified
        if not hasattr(meta, 'model'):
            raise RuntimeError(
                'Query %s.%s does not define a model' % (
                    attrs['__module__'], name
                )
            )

        # Validate that the specified model is a Django model
        model = getattr(meta, 'model')
        if not inspect.isclass(model):
            raise RuntimeError(
                'Query %s.%s.Meta defines a non-class model' % (
                    attrs['__module__'], name
                )
            )
        if not issubclass(model, models.Model):
            raise RuntimeError(
                'Query %s.%s defines a non-Django model class' % (
                    attrs['__module__'], name
                )
            )

        # Get or set the _meta QuerySet object
        queryset = getattr(meta, 'queryset', None)
        if queryset is None:
            queryset = model._default_manager.all()
            setattr(meta, 'queryset', queryset)

        # Add all attributes to the class.
        for obj_name, obj in attrs.items():
            new_class.add_to_class(obj_name, obj)

        # Parse and set fields
        for field_name in getattr(meta, 'fields', []):
            field = new_class.get_field(field_name)
            new_class.add_to_class(field_name, field)

        return new_class

    def add_to_class(cls, name, value):
        # We should call the contribute_to_class method only if it's bound
        if not inspect.isclass(value) and hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)

    def get_field(cls, field_name, model=None, queryset=None):
        """
        Look up the query field of the specified field. The specified field can
        be either an actual field, or some kind of database function that is
        defined through the Django ORM. If the model parameter is not specified,
        the lookup will be done on the model defined in the Query's Meta-class.

        TODO:
            * Should also support annotated fields on the queryset

        :param field_name: The field name to look up
        :param model: The model to look up the field on (optional)
        """
        model = cls._meta.model if not model else model
        queryset = cls._meta.queryset if queryset is None else queryset

        # If the field does not contain the lookup separator, simply try to get
        # the field. If this fails, the field does not exists.
        if LOOKUP_SEP not in field_name:
            field = model._meta.get_field(field_name)
            field_class = type(field)
            if field_class in FIELD_FOR_DBFIELD_DEFAULTS:
                f = FIELD_FOR_DBFIELD_DEFAULTS[field_class]
                # TODO: Verbose name etc.
                return f['field_class']()
            else:
                raise ValueError('Unsupported field: %s' % field)

        # The field contained the lookup separator, so we split and try to
        # locate the field based on the first part of the field name.
        field_name, rest = field_name.split(LOOKUP_SEP, 1)
        field = model._meta.get_field(field_name)

        # If field is a relation, we have to resolve it
        if field.is_relation:
            # TODO: Try to set a reasonable verbose name?
            related_model = field.related_model
            related_queryset = related_model._default_manager.all()
            return cls.get_field(rest, related_model, related_queryset)

        # It's not a relational field, so 'rest' must be one or more transforms
        query = queryset.query
        transforms = rest.split(LOOKUP_SEP)
        for i, transform_name in enumerate(transforms):
            transform = field.get_transform(transform_name)

            # Check that we actually found a transform
            if not transform:
                raise ValueError('Unknown transform %s on %s' % (
                    transform_name, field
                ))

            # If it's not the last transform, we should resolve the output
            # field, as the next transform will be on the output field of this
            # transform.
            if i + 1 < len(transforms):
                field = _get_output_field(field, transform_name, query)
                field_name = field_name + LOOKUP_SEP + transform_name

        # Return query field based on transform class
        if transform in FIELD_FOR_DBFUNCTION_DEFAULTS:
            f = FIELD_FOR_DBFUNCTION_DEFAULTS[transform]
            # TODO: Verbose name etc.
            return f['field_class']()
        else:
            field = _get_output_field(field, transform_name, query)
            field_class = type(field)
            if field_class not in FIELD_FOR_DBFIELD_DEFAULTS:
                raise ValueError('Unsupported transform %s on %s' % (
                    transform, field
                ))
            f = FIELD_FOR_DBFIELD_DEFAULTS[field_class]
            # TODO: Verbose name etc.
            return f['field_class']()


class Query(metaclass=QueryBase):
    """
    This is the class responsible for converting a JSON object into a Query
    object. As it parses the object, it will validate that the query
    spesification is valid. The parsing process is stateless, so a query object
    can safely be reused and used in multiple threads at the same time.

    In addition to providing parsing of the queries, the query also provides a
    method that will return an object describing the allowed queries and
    parameters. This can be used to present dynamic user interfaces.

    A new Query sub-class should be created for each Django model. The
    sub-class is responsible for registering the model and optionally what
    fields and operations are allowed to be queried.
    """

    def __init__(self, query):
        self.condition = self.resolve_condition(query)

    @property
    def is_valid(self):
        """
        Check if this query is valid.
        """
        return self.condition.is_valid()

    def get_queryset(self):
        """
        Get a queryset of the objects that match this query.
        """
        assert self.is_valid, 'Cannot get queryset from invalid query'
        return self.condition.filter(self._meta.queryset)

    @classmethod
    def register_condition(cls, condition):
        """
        Register a new condition kind for this query.

        :param condition: The condition class to register
        """
        assert issubclass(condition, conditions.Condition)
        cls._meta.conditions[condition.kind] = condition

    @classmethod
    def get_condition(cls, kind):
        """
        Get a condition based on the specified kind

        :param kind: Condition kind to get
        """
        return cls._meta.conditions.get(kind, None)

    @property
    def specification(self):
        return self.fields


    #
    # "Private" methods
    #

    def resolve_condition(self, query):
        """
        Resolve the given query into a condition.

        :param query: The query to resolve
        """
        # Copy the query, to make sure we don't modify the original query object
        query = query.copy()

        # Locate the query class
        kind = query.pop('kind', None)
        if not kind:
            raise ValueError('Condition kind not specified')
        Condition = self.get_condition(kind)
        if not Condition:
            raise ValueError('Unsupported condition: %s' % kind)

        # Return query object
        return Condition(query=self, **query)
