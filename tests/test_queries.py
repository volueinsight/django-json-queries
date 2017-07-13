import pytest

from .queries import ProductQuery


@pytest.mark.parametrize('query,is_valid,result_count', [
    ({}, False, None),
])
def test_product_query(test_products, query, is_valid, result_count):
    q = ProductQuery(query)
    assert q.is_valid == is_valid

    if is_valid:
        assert q.get_queryset().count() == result_count
