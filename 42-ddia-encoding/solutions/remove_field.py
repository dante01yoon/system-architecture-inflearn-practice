"""연습 문제 풀이: v3에서 customer(번호 2)를 지우고, 그 번호를 다시 쓰지 않게 막는다(프로토콜 버퍼의 reserved와 같은 생각)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from codec import V2, decode, encode  # noqa: E402

RESERVED = {2}
V3 = {k: v for k, v in V2.items() if k != 2}


def add_field(schema, tag, field):
    assert tag not in schema and tag not in RESERVED, f"번호 {tag}는 예전에 쓰던 번호라 다시 쓸 수 없음"
    return {**schema, tag: field}


order = {"order_id": 1042, "customer": "minji", "books": ["DDIA"], "total": 28800, "gift_wrap": False}
got, skipped = decode(encode(order, V2), V3)
print(f"1) v2가 쓴 주문을 v3가 읽기: 번호 {skipped} 건너뜀, 나머지 {got}")
got, _ = decode(encode({k: v for k, v in order.items() if k != "customer"}, V3), V2)
print(f"2) v3가 쓴 주문을 v2가 읽기: customer 기본값 {got['customer']!r}")
try:
    add_field(V3, 2, ("coupon", "str"))
except AssertionError as e:
    print(f"3) {e}")
