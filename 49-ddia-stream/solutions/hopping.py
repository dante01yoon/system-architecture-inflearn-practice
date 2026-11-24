"""연습 문제 풀이: 호핑 윈도(1분 창, 30초마다 새 창). 한 이벤트가 창 두 개에 들어간다. 늦은 이벤트 처리는 빼고 개념만."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from stream import SALES, clock  # noqa: E402


def hopping(events, size=60, hop=30):
    out = {}
    for t, _, won in events:
        first = (t - size) // hop * hop + hop        # t를 품는 가장 이른 창의 시작
        for start in range(max(first, 0), t + 1, hop):
            out.setdefault(start, []).append(won)
    return sorted(out.items())


if __name__ == "__main__":
    for start, wons in hopping(SALES):
        print(f"{clock(start)}~{clock(start + 60)}  {len(wons)}건  {sum(wons):7,}원")
    assert sum(len(w) for _, w in hopping(SALES)) == 2 * len(SALES) - sum(t < 30 for t, _, _ in SALES)
