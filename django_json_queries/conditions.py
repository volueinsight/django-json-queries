from functools import reduce

from django.db.models import Q


__all__ = [
    'Condition',
    'AndCondition', 'OrCondition',
    'LookupCondition',
]


class Condition:
    def __init__(self, query, *args, **kwargs):
        self.query = query

    def annotate(self, queryset):
        """
        Hook for conditions (or filters) that need to annotate the queryset.
        This method will be called before the filter method, to ensure that all
        annotations are in place when filters are added.

        NOTE:
            This method is at the moment just a workaround for Django's missing
            support for filtering on 'Exists'-querys. When support for that is
            added, this method will probably be removed.

        :param queryset: The queryset to annotate
        :returns: A queryset with any required annotations added
        """
        return queryset

    def filter(self, queryset):
        """
        Add this condition and return a new queryset

        :param queryset: The queryset to filter
        """
        return self.annotate(queryset).filter(self.get_filter())


class AndCondition(Condition):
    kind = 'and'

    def __init__(self, *args, conditions=None, **kwargs):
        super().__init__(*args, **kwargs)

        assert isinstance(conditions, list) and len(conditions) > 0, \
            'Conditions must be a list with at least one element'

        self.conditions = [self.query.resolve_condition(c) for c in conditions]

    def annotate(self, queryset):
        """
        Allow subqueries to add their annotations
        """
        for c in self.conditions:
            queryset = c.annotate(queryset)
        return queryset

    def get_filter(self):
        def reduce_and(a, b):
            return Q(a & b)

        # Return filtered queryset
        return reduce(reduce_and, [c.get_filter() for c in self.conditions])


class OrCondition(Condition):
    kind = 'or'

    def __init__(self, *args, conditions=None, **kwargs):
        super().__init__(*args, **kwargs)

        assert isinstance(conditions, list) and len(conditions) > 0, \
            'Conditions must be a list with at least one element'

        self.conditions = [self.query.resolve_condition(c) for c in conditions]

    def annotate(self, queryset):
        """
        Allow subqueries to add their annotations
        """
        for c in self.conditions:
            queryset = c.annotate(queryset)
        return queryset

    def get_filter(self):
        def reduce_or(a, b):
            return Q(a | b)

        # Return filtered queryset
        return reduce(reduce_or, [c.get_filter() for c in self.conditions])


class LookupCondition(Condition):
    kind = 'lookup'

    def __init__(self, *args, field=None, lookup=None, value=None, **kwargs):
        super().__init__(*args, **kwargs)

        assert isinstance(field, str), \
            'field must be specified'
        assert isinstance(lookup, str), \
            'lookup must be specified'

        self.field = getattr(self.query, field)
        self.lookup = lookup
        self.value = value

    def get_filter(self):
        field = '%s__%s' % (self.field.model_name, self.lookup)
        return Q(**{field: self.field.prepare(self.value, self.lookup)})
