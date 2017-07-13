import pytest

from datetime import date

from django.utils.timezone import make_aware

from .models import Product, Manufacturer


@pytest.fixture()
def test_products(db):
    m1 = Manufacturer.objects.create(name='Manufacturer 1')
    m2 = Manufacturer.objects.create(name='Manufacturer 2')

    # m1 products
    Product.objects.create(
        name='Green left sock',
        released=date(2017,1,1),
        manufacturer=m1,
    )
    Product.objects.create(
        name='Blue right sock',
        released=date(2016,6,1),
        manufacturer=m1,
    )
    Product.objects.create(
        name='Red sock pair',
        released=date(2017,6,1),
        manufacturer=m1,
    )

    # m2 products
    Product.objects.create(
        name='Blue pants',
        released=date(2017,6,1),
        manufacturer=m2,
    )
