"""연습 문제 풀이: 질문 하나(백업 복구 연습)를 더하고 답이 없을 때 순위가 어디에 오는지."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from answers import ANSWERS  # noqa: E402
from checklist import CHECKLIST  # noqa: E402
from scorer import risks  # noqa: E402

more = CHECKLIST + [("F3", "장애", "주문 DB 백업에서 실제로 복구해 봤나", "H")]
for score, lvl, qid, area, question, note in risks(more, ANSWERS):
    print(f"[{lvl}] {score} {qid} {area} {note}")
