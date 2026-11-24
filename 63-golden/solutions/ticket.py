"""연습 풀이: 포화를 앞선 신호로. DB 풀 사용률이 70%를 넘으면 사람을 깨우지 않는 티켓을 남긴다."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from log import hour  # noqa: E402
from signals import pages, signals  # noqa: E402

rows = [signals(r) for r in hour()]
ticket = next(m for m, r in enumerate(rows) if r["sat"] > 70)
page = pages(rows)[0]
print(f"티켓(포화 {rows[ticket]['sat']:.0f}%): {ticket}분")
print(f"페이지(오류율 {rows[page]['err']:.1f}%): {page}분")
print(f"→ {page - ticket}분 먼저 알았다")
