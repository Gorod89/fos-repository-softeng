from decimal import Decimal

import pytest

from order_service.service import Order, total


def test_total_uses_decimal_and_discount() -> None:
    order = Order(quantity=3, unit_price=Decimal("10.00"))
    assert total(order, Decimal("10")) == Decimal("27.00")


def test_invalid_discount_is_rejected() -> None:
    with pytest.raises(ValueError, match="от 0 до 100"):
        total(Order(quantity=1, unit_price=Decimal("1")), Decimal("101"))
