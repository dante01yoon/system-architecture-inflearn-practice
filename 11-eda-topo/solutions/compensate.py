"""연습 문제 풀이: 브로커 토폴로지에서 카드가 거절되면 재고를 되돌리기 — 실패도 이벤트로 올리고, 재고 서비스가 그것을 구독한다."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import shop  # noqa: E402
from broker import Broker  # noqa: E402


def payment_service(msg, broker):
    try:
        shop.charge(msg)
    except ValueError as e:
        broker.publish("payment.failed", {**msg, "reason": str(e)})  # 다시 시도하지 않고 실패를 알린다
        return
    broker.publish("payment.done", msg)


def stock_compensator(msg, broker):
    shop.restock(msg)


b = Broker()
b.subscribe("order.placed", shop.stock_service)
b.subscribe("stock.reserved", payment_service)
b.subscribe("payment.failed", stock_compensator)
b.publish("order.placed", {"id": 3, "book": "DDIA", "qty": 1, "card": "거절"})
print("흐름:", " / ".join(b.trace))
print("남은 재고 DDIA:", shop.stock["DDIA"], "권 (원래 5권)")
