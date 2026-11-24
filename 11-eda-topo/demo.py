"""같은 주문 흐름을 브로커와 미디에이터로 돌려 보고, 독이 든 메시지가 DLQ로 가는 것을 본다."""
import shop
from broker import Broker
from mediator import Mediator


def wire():
    b = Broker()
    b.subscribe("order.placed", shop.stock_service)
    b.subscribe("stock.reserved", shop.payment_service)
    b.subscribe("payment.done", shop.mail_service)
    b.subscribe("payment.done", shop.report_service)
    return b


def main():
    print("1) 브로커: 주문 #1 (DDIA 2권)")
    b = wire()
    b.publish("order.placed", {"id": 1, "book": "DDIA", "qty": 2})
    for line in b.trace:
        print(f"   {line}")
    print(f"   흐름 전체를 아는 곳: 없음 (구독 {sum(map(len, b.subs.values()))}개에 흩어짐)")

    print("2) 미디에이터: 주문 #2 (DDIA 1권)")
    m = Mediator([("재고", shop.reserve, shop.restock), ("결제", shop.charge, shop.nothing),
                  ("알림", shop.notify, shop.nothing)])
    result = m.run({"id": 2, "book": "DDIA", "qty": 1})
    print(f"   지휘자 기록: {' -> '.join(m.log)}")
    print(f"   결과: {result}, 남은 재고 DDIA {shop.stock['DDIA']}권")

    print("3) 카드 거절: 주문 #3 (DDIA 1권)")
    wire().publish("order.placed", {"id": 3, "book": "DDIA", "qty": 1, "card": "거절"})
    print(f"   브로커: 남은 재고 DDIA {shop.stock['DDIA']}권 (잡아 둔 재고가 그대로)")
    shop.restock({"book": "DDIA", "qty": 1})  # 비교를 위해 원래대로
    result = m.run({"id": 3, "book": "DDIA", "qty": 1, "card": "거절"})
    print(f"   미디에이터: {result}, 남은 재고 DDIA {shop.stock['DDIA']}권")

    print("4) 독이 든 메시지: 주문 #4 (권수가 '두 권')")
    b = wire()
    b.publish("order.placed", {"id": 4, "book": "DDIA", "qty": "두 권"})
    b.publish("order.placed", {"id": 5, "book": "Refactoring", "qty": 1})
    print(f"   DLQ에 남은 메시지: {', '.join('주문 #%d' % msg['id'] for _, _, msg in b.dead)}")
    print(f"   뒤 주문 #5는 그대로 진행: 결제된 주문 {shop.paid}")


if __name__ == "__main__":
    main()
