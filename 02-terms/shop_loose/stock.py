"""재고: 「주문됨」을 듣고 줄인다. 바닥나면 「품절」 이벤트를 남긴다."""
from shop_loose import events

shelf = {"Clean Architecture": 3}


def on_order_placed(order):
    shelf[order["book"]] -= order["qty"]
    if shelf[order["book"]] == 0:
        events.publish("SoldOut", order["book"])


events.subscribe("OrderPlaced", on_order_placed)
