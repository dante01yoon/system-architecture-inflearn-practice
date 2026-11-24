"""결제: 환불할 때 주문 모듈과 재고 모듈까지 직접 건드린다."""
from shop_tight import orders, stock

charged = []


def charge(customer, amount):
    charged.append((customer, amount))


def refund(order):
    stock.release(order["book"], order["qty"])
    charged.append((order["customer"], -order["qty"] * order["price"]))
    return f"환불: {orders.format_order(order)}"
