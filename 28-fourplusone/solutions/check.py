"""연습 문제 풀이: 「주문 취소하기」 시나리오를 더하고, 걸린 불일치를 고친다."""
import copy
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from bookshop import MODEL  # noqa: E402
from fourplusone import walk  # noqa: E402

CANCEL = [
    {"step": "취소 요청", "logical": "Order", "process": "web", "development": "shop/web"},
    {"step": "환불하기", "logical": "Refund", "process": "payment-gw", "development": "shop/payment"},
]
m = copy.deepcopy(MODEL)
print("고치기 전:", [(s, b) for _, s, b in walk(m, CANCEL) if b])
m["logical"]["Refund"] = ["Payment"]            # 논리 뷰에 환불 클래스 추가
print("고친 뒤:", [(s, b) for _, s, b in walk(m, CANCEL) if b])
