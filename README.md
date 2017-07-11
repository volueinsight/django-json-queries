# Django JSON queries

Django-json-queries is a reusable [Django](https://djangoproject.com)
application allowing users to easily add support for running complex queries
specified in JSON against a model or queryset.


## Requirements

 * **Python**: 3
 * **Django**: 1.11

## Installation

Install using pip:

```sh
pip install django-json-queries
```

Then add `django_json_queries` to your `INSTALLED_APPS`.

```python
INSTALLED_APPS = [
    ...
    'django_json_queries',
]
```

## Usage

The interface for django-json-queries is similar to that used by Django's
`ModelForms` and also the
[django-filter](https://github.com/carltongibson/django-filter) package which
specify filters in a similar way.

A `Query` subclass must be set up for each model that you want to filter, say
we have a Product model, then a query can be set up with this code:

```python
import django_json_queries

class ProductQuery(django_json_queries.Query):
    class Meta:
        model = Product
        fields = ['name', 'price', 'manufacturer']
```

And you can then use this in you view:

```python
def product_query(request):
    queryset = ProductQuery(json.loads(request.body)).get_queryset()
    return render(request, 'my_app/template.html', {'queryset': queryset})
```

An example request would look something like this:

```http
POST /api/products/query HTTP/1.1
Content-Type: application/json

{
    "kind": "lookup",
    "field": "name",
    "lookup": "exact",
    "value": "Green left shoe"
}
```
