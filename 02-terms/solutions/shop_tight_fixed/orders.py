from shop_tight_fixed import email, payment, stock


def place_order(customer, book, qty, price):
    left = stock.reserve(book, qty)
    if left == 0:
        email.send_admin(f"{book} 품절")
    payment.charge(customer, qty * price)
    order = {"customer": customer, "book": book, "qty": qty, "price": price}
    email.send(customer, f"주문 완료: {format_order(order)}")
    return order


def format_order(order):
    return f"{order['book']} {order['qty']}권"
