from django_json_queries import Query

from .models import Product


class ProductQuery(Query):
    class Meta:
        model = Product
        fields = [
            'name',
            'released',
            'released__year',
            'manufacturer__name',
        ]
