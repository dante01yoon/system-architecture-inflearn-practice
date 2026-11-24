"""같은 '책'이 컨텍스트마다 다른 모델이 되고, 주문 애그리거트가 규칙을 지키는 모습."""
from dataclasses import fields

from catalog import SHELF
from ordering import Order, Rejected
from translate import add_to_order, to_parcels

ISBN = "9780134494166"


def names(obj):
    return ", ".join(f.name for f in fields(obj))


def try_(what, fn):
    try:
        fn()
        print(f"   {what} -> 통과")
    except Rejected as e:
        print(f"   {what} -> 거절: {e}")
    except AttributeError as e:  # 튜플·frozen 줄은 바꿀 수 없다
        print(f"   {what} -> 거절: {type(e).__name__}")


def main():
    order = Order("A-1")
    add_to_order(order, SHELF[ISBN], 2)
    print("1) 같은 ISBN, 컨텍스트마다 다른 책")
    print(f"   카탈로그 Book : {names(SHELF[ISBN])}")
    print(f"   주문 OrderLine: {names(order.lines[0])}")
    print(f"   배송 Parcel   : {names(to_parcels(order)[0])}")

    print("2) 루트로 담기")
    add_to_order(order, SHELF["9781680502398"], 3)
    print(f"   주문 {order.order_id}: {sum(x.qty for x in order.lines)}권, 합계 {order.total():,}원")

    print("3) 바깥에서 직접 바꾸기")
    try_("lines에 줄 끼워 넣기", lambda: order.lines.append("책"))
    try_("줄의 권수를 99로", lambda: setattr(order.lines[0], "qty", 99))

    print("4) 루트를 거쳐도 규칙은 지킨다")
    try_("6권 더 담기(모두 11권)", lambda: add_to_order(order, SHELF[ISBN], 6))
    try_("200,000원 할인", lambda: order.discount(200000))
    try_("10,000원 할인", lambda: order.discount(10000))
    print(f"   주문 {order.order_id}: {sum(x.qty for x in order.lines)}권, 합계 {order.total():,}원")

    print("5) 주문 -> 배송으로 번역")
    for p in to_parcels(order):
        print(f"   {p.isbn} · {p.weight_g}g × {p.qty}")


if __name__ == "__main__":
    main()
