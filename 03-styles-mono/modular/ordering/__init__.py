"""주문 모듈: 다른 모듈은 공개 함수로만 부른다."""
from modular import catalog, coupons

_ORDERS = []


def place_order(req):
    amount = catalog.price_of(req["title"]) * req["qty"]
    amount -= coupons.discount(req.get("coupon", ""), amount)
    _ORDERS.append((req["title"], req["qty"], amount))
    return amount
