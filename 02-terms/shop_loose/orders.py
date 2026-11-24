"""주문: 누가 듣는지 모른 채 「주문됨」 이벤트만 남긴다."""
from shop_loose import events


def place_order(customer, book, qty, price):
    order = {"customer": customer, "book": book, "qty": qty, "price": price}
    events.publish("OrderPlaced", order)
    return order
