"""같은 주문 흐름을 코레오그래피와 오케스트레이션으로: 둘 다 성공, 둘 다 결제 실패, 흐름은 어디서 읽나."""
import sys

import choreography
import orchestration
from bus import Bus
from shop import Shop


def choreo(order):
    bus, shop = Bus(), Shop()
    choreography.wire(bus, shop).place(order)
    bus.run()
    return bus, shop


def orches(order, flaky=0):
    bus, shop = Bus(), Shop(flaky=flaky)
    saga = orchestration.OrderSaga(bus, shop)
    orchestration.Participant(bus, shop)
    saga.start(order)
    bus.run()
    return saga, shop


def main(part=""):
    # 녹화 터미널은 19줄 — 1은 1)·2), 2는 3)·4)(인자 없으면 전부)
    if part != "2":
        part12()
    if part != "1":
        part34()


def part12():
    print("1) 코레오그래피: 주문 #1 (DDIA 1권)")
    bus, shop = choreo({"id": 1, "book": "DDIA", "qty": 1})
    for line in bus.trace:
        print(f"   {line}")
    print(f"   주문 #1: {shop.orders[1]}, 남은 재고 {shop.stock['DDIA']}권")

    print("2) 오케스트레이션: 주문 #2 (배송사가 한 번 응답 없음)")
    saga, shop = orches({"id": 2, "book": "DDIA", "qty": 1}, flaky=1)
    print("   Saga 기록:")
    for line in saga.log:
        print(f"     {line}")
    print(f"   주문 #2: {shop.orders[2]}, 남은 재고 {shop.stock['DDIA']}권")


def part34():
    print("3) 결제 실패: 주문 #3 (카드 거절), 두 방식 모두")
    bus, shop = choreo({"id": 3, "book": "DDIA", "qty": 1, "card": "거절"})
    print(f"   코레오그래피: {', '.join(bus.trace)}")
    print(f"     → 주문 #3: {shop.orders[3]}, 재고 {shop.stock['DDIA']}권 그대로")
    saga, shop = orches({"id": 3, "book": "DDIA", "qty": 1, "card": "거절"})
    print(f"   오케스트레이션: {' -> '.join(saga.log)}")
    print(f"     → 주문 #3: {shop.orders[3]}, 재고 {shop.stock['DDIA']}권 그대로")

    print("4) 흐름을 이해하려면 어디를 읽나")
    subs = sum(map(len, bus.subs.values()))
    print(f"   코레오그래피: choreography.py의 서비스 4개, 구독 {subs}개를 이어 따라가기")
    print(f"   오케스트레이션: orchestration.py의 STEPS {len(orchestration.STEPS)}줄 한 곳")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
