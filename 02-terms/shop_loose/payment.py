"""결제: 「주문됨」을 듣고 결제한다."""
from shop_loose import events

charged = []


def on_order_placed(order):
    charged.append((order["customer"], order["qty"] * order["price"]))


events.subscribe("OrderPlaced", on_order_placed)
