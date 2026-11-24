"""서점 주문 3건을 두 방식의 OrderPlaced로 보내고, 되묻기 호출 수를 센다. 끝으로 이벤트 소싱 되감기."""
from bookshop import (OrderService, mail_by_notification, mail_by_state, notification,
                      ship_by_notification, ship_by_state, state_transfer)
from sourcing import EVENTS, apply

ORDERS = [(1, "민지", {"Clean Architecture": 1}, "서울"),
          (2, "준호", {"DDIA": 2}, "부산"),
          (3, "서연", {"Refactoring": 1, "DDIA": 1}, "대전")]


def shop():
    s = OrderService()
    for o in ORDERS:
        s.place(*o)
    return s


def main():
    s = shop()
    print("1) 주문 3건, 소비자 2곳(배송·메일)")
    print(f"2) 방식 1 이벤트 알림: {notification(s.orders[1])}")
    for o in s.orders.values():
        ship_by_notification(notification(o), s), mail_by_notification(notification(o), s)
    print(f"   되묻기 호출 {s.calls}번 (주문 3 x 소비자 2)")

    s, ship, mail = shop(), {}, {}
    print(f"3) 방식 2 상태 전달: 이벤트 하나에 칸 {len(state_transfer(s.orders[1]))}개")
    for o in s.orders.values():
        ship_by_state(state_transfer(o), ship), mail_by_state(state_transfer(o), mail)
    print(f"   되묻기 호출 {s.calls}번, 소비자 쪽 사본 {len(ship) + len(mail)}벌")

    print("4) 주문 서비스가 멈추면 배송은?")
    s.up = False
    ok = fail = 0
    for o in s.orders.values():
        try:
            ship_by_notification(notification(o), s)
            ok += 1
        except ConnectionError:
            fail += 1
    print(f"   방식 1: 성공 {ok}건, 실패 {fail}건")
    print(f"   방식 2: 성공 {len([ship_by_state(state_transfer(o), {}) for o in s.orders.values()])}건, 실패 0건")

    print("5) 이벤트 소싱: 이벤트 3개를 차례로 다시 적용")
    state = {}
    for e in EVENTS:
        state = apply(state, e)
        paid = f", 결제 {state['paid']:,}원" if "paid" in state else ""
        print(f"   {e['type']:<12} -> {state['status']}, 책 {sum(state['books'].values())}권{paid}")


if __name__ == "__main__":
    main()
