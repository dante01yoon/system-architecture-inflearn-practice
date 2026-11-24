"""풀이 예시: 분야별 상위 3권. 분야 = 책 번호 끝자리(가정). 분야마다 Leaderboard를 하나씩 둔다."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from stream import purchases  # noqa: E402
from topk import Leaderboard  # noqa: E402

boards = {g: Leaderboard(4) for g in "0123456789"}
for t, b in purchases():
    boards[b[-1]].add(t, b)
for g, board in boards.items():
    print(f"분야 {g}: " + " · ".join(f"{b} {n:,}" for b, n in board.top(3, 5400)))
