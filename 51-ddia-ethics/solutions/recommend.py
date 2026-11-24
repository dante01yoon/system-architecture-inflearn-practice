"""연습 풀이: 「추천」 목적을 더한다. 추천에는 누가(가명) 무엇을 샀는지만 필요하다 — 가격·날짜도 빼고, 생일·주소는 당연히 뺀다."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from demo import RAW  # noqa: E402
from privacy import PURPOSE, minimize  # noqa: E402

PURPOSE["추천"] = ["user", "book"]

if __name__ == "__main__":
    events = [minimize(r, "추천") for r in RAW]
    for e in events:
        print(e)
    assert all(list(e) == ["user", "book"] for e in events)
