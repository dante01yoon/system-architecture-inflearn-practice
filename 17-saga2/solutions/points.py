"""연습 문제 풀이: 결제 뒤에 「포인트 적립」 단계를 더하면, 두 방식에서 각각 어디를 고치나.
실행: python3 solutions/points.py (saga2 폴더에서)"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import choreography  # noqa: E402
import orchestration  # noqa: E402
from bus import Bus  # noqa: E402
from shop import Shop  # noqa: E402


# 코레오그래피: 새 서비스가 PaymentDone을 구독하고, 실패 이벤트(StockFailed)도 구독해 스스로 되돌려야 한다
class PointService:
    def __init__(self, bus, shop):
        self.shop, shop.points = shop, {}
        bus.subscribe("PaymentDone", lambda o: shop.points.__setitem__(o["id"], 10))
        bus.subscribe("StockFailed", lambda o: shop.points.pop(o["id"], None))


bus, shop = Bus(), Shop()
order = choreography.wire(bus, shop)
PointService(bus, shop)
order.place({"id": 1, "book": "DDIA", "qty": 9})   # 재고 부족 → 포인트도 되돌려야
bus.run()
print(f"코레오그래피: 새 클래스 1개 + 구독 2개, 재고 실패 뒤 포인트 {shop.points}")

# 오케스트레이션: STEPS에 한 줄, 참여자에 커맨드 둘
orchestration.STEPS.insert(1, ("포인트", "point.add", "point.remove", False))
bus, shop = Bus(), Shop()
shop.points = {}
saga = orchestration.OrderSaga(bus, shop)
orchestration.Participant(bus, shop)
bus.subscribe("point.add", lambda o: (shop.points.__setitem__(o["id"], 10), bus.publish("saga.reply", {"ok": True})))
bus.subscribe("point.remove", lambda o: shop.points.pop(o["id"], None))
saga.start({"id": 1, "book": "DDIA", "qty": 9})
bus.run()
print(f"오케스트레이션: STEPS 1줄 + 커맨드 2개, 기록 {' -> '.join(saga.log)}, 포인트 {shop.points}")
