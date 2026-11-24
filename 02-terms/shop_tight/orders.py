"""주문: 재고·결제·메일을 직접 부른다."""
from shop_tight import email, payment, stock


def place_order(customer, book, qty, price):
    stock.reserve(book, qty)
    payment.charge(customer, qty * price)
    order = {"customer": customer, "book": book, "qty": qty, "price": price}
    email.send_receipt(order)
    return order


def format_order(order):
    return f"{order['book']} {order['qty']}권"
