"""연습 문제 풀이: 쿠폰 할인이 생겨 주문에 discount 칸이 붙었을 때, 두 방식에서 무엇을 고쳐야 하나."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bookshop import OrderService, notification, state_transfer  # noqa: E402

s = OrderService()
s.place(1, "민지", {"DDIA": 2}, "서울")
s.orders[1]["discount"] = 0.1
print("방식 1 이벤트:", notification(s.orders[1]), "-> 이벤트는 그대로, 필요한 소비자가 get_order로 읽는다")
print("방식 2 이벤트:", state_transfer(s.orders[1]), "-> 칸이 늘었다: 소비자 사본·스키마도 같이 맞춰야 한다")
