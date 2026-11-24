"""연습 풀이: 선물 포장(2,000원)을 주문 애그리거트 안에서만 붙인다. 루트의 add를 거치게 해 10권 규칙을 그대로 지킨다."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from catalog import SHELF  # noqa: E402
from ordering import Order, Rejected  # noqa: E402
from translate import add_to_order  # noqa: E402


class GiftOrder(Order):
    WRAP = 2000

    def wrap(self):
        if not self._lines:
            raise Rejected("빈 주문은 포장할 수 없음")
        self.add("WRAP", "선물 포장", self.WRAP, 1)  # add를 거치니 10권 규칙도 그대로


o = GiftOrder("G-1")
add_to_order(o, SHELF["9780134494166"], 1)
o.wrap()
assert o.total() == 34000, o.total()
print("선물 포장 포함 합계", f"{o.total():,}원")
