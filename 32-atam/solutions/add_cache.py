"""연습 문제 풀이: 「책 목록 캐시 10분」 결정을 더하고 분류·위험을 다시 본다.
캐시는 검색을 빠르게 하지만(성능+), 재고가 바뀐 걸 늦게 보여 준다(정확성-). 정확성 시나리오를 트리에 더해야 위험이 보인다."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tree import DECISIONS, TREE, classify, risks  # noqa: E402

tree = TREE + [("정확성", "재고 표시", "C1", "품절된 책은 1분 안에 품절로 보인다", "H", "H")]
decisions = {**DECISIONS, "책 목록 캐시 10분": {"성능": +1, "정확성": -1}}
assert classify(decisions["책 목록 캐시 10분"]) == "트레이드오프"
assert ("책 목록 캐시 10분", "C1", "정확성") in risks(tree, decisions)
print(classify(decisions["책 목록 캐시 10분"]), [r for r in risks(tree, decisions) if r[0] == "책 목록 캐시 10분"])
