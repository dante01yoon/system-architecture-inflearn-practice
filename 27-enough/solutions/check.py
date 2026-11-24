"""연습 문제 풀이: 기준을 9점으로 올리고, 결제 응답 지연에 두 번째 기법(주문 큐)을 쓴 뒤 다시 매긴다."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from enough import evaluate, load, plan  # noqa: E402

risks = load(os.path.join(os.path.dirname(__file__), "..", "risks.csv"))
print("기준 9점:", [(r["risk"], t) for r, t in plan(risks, threshold=9)])
pay = next(r for r in risks if r["risk"] == "결제 응답 지연")
pay["likelihood"], pay["after"] = pay["after"], 1   # 부하 테스트 뒤 가능성 2 → 큐를 붙인 뒤 1
print("큐를 붙인 뒤:", [(r["risk"], b, a, "남음" if left else "충분") for r, b, a, left in evaluate(risks)])
