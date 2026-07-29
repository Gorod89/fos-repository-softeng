from decimal import Decimal

from pydantic import BaseModel, Field


class Order(BaseModel):
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(gt=0)


def total(order: Order, discount_percent: Decimal = Decimal("0")) -> Decimal:
    if not Decimal("0") <= discount_percent <= Decimal("100"):
        raise ValueError("Скидка должна быть от 0 до 100 процентов.")
    return (order.quantity * order.unit_price * (Decimal("100") - discount_percent) / 100).quantize(
        Decimal("0.01")
    )
