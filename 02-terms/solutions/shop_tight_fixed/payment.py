from shop_tight_fixed import orders, stock

charged = []


def charge(customer, amount):
    charged.append((customer, amount))


def refund(order):
    stock.release(order["book"], order["qty"])
    charged.append((order["customer"], -order["qty"] * order["price"]))
    return f"환불: {orders.format_order(order)}"
