"""같은 OrderPlaced를 두 방식으로 보낸다: 알림만 보내기 대 상태를 실어 보내기."""


class OrderService:
    """주문 원본을 가진 서비스. get_order가 불릴 때마다 calls를 센다."""

    def __init__(self):
        self.orders, self.calls, self.up = {}, 0, True

    def place(self, order_id, customer, books, address):
        order = {"id": order_id, "customer": customer,
                 "books": books, "address": address}
        self.orders[order_id] = order

    def get_order(self, order_id):
        if not self.up:
            raise ConnectionError("주문 서비스 응답 없음")
        self.calls += 1
        return dict(self.orders[order_id])


def notification(order):
    """방식 1 이벤트 알림: 무슨 일이 있었는지만."""
    return {"type": "OrderPlaced", "order_id": order["id"]}


def state_transfer(order):
    """방식 2 상태를 실은 이벤트: 소비자가 쓸 값까지."""
    return {"type": "OrderPlaced", **order}


def ship_by_notification(event, orders):
    order = orders.get_order(event["order_id"])  # 되묻기: 호출 한 번
    return f"{order['address']}로 {sum(order['books'].values())}권"


def ship_by_state(event, copy):
    copy[event["id"]] = {k: event[k] for k in ("address", "books")}  # 내 사본
    return f"{event['address']}로 {sum(event['books'].values())}권"


def mail_by_notification(event, orders):
    return f"{orders.get_order(event['order_id'])['customer']}님께 메일"


def mail_by_state(event, copy):
    copy[event["id"]] = {"customer": event["customer"]}
    return f"{event['customer']}님께 메일"
