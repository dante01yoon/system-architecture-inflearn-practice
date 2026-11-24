"""서점 서비스들: 재고, 결제, 알림. 브로커용 처리기와 미디에이터용 단계가 같은 일을 한다."""
stock = {"DDIA": 5, "Refactoring": 1}
paid, sent = [], []


def reserve(order):
    if not isinstance(order["qty"], int):
        raise TypeError("권수가 숫자가 아님")
    if stock[order["book"]] < order["qty"]:
        raise ValueError("재고 부족")
    stock[order["book"]] -= order["qty"]


def restock(order):
    stock[order["book"]] += order["qty"]


def charge(order):
    if order.get("card") == "거절":
        raise ValueError("카드 거절")
    paid.append(order["id"])


def notify(order):
    sent.append(order["id"])


def nothing(order):
    pass


# 브로커 쪽: 각자 일을 하고, 끝났다는 처리 이벤트를 다시 올린다
def stock_service(msg, broker):
    reserve(msg)
    broker.publish("stock.reserved", msg)


def payment_service(msg, broker):
    charge(msg)
    broker.publish("payment.done", msg)


def mail_service(msg, broker):
    notify(msg)


def report_service(msg, broker):
    pass  # 매출 집계: 같은 이벤트를 한 부 더 받는다
