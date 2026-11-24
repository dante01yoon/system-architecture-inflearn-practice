"""python3 demo.py 1 → 샤드 카운터 + 1시간 창 + 힙 합치기,  2 → count-min sketch 추정 대 정확"""
import sys
from collections import Counter

from sketch import CountMin
from stream import BOOKS, purchases
from topk import Leaderboard, exact_top

HOT = ("책99999", "책00001")


def load(writes):
    return " · ".join(f"{w:,}" for w in writes), max(writes) / (sum(writes) / len(writes))


def ranking():
    events = purchases()
    print(f"1) 주문 {len(events):,}건 · 90분 · 책 {BOOKS:,}권 · 샤드 4개")
    for i, hot in enumerate([(), HOT]):
        board = Leaderboard(4, hot)
        for t, b in events:
            board.add(t, b)
        text, ratio = load(board.writes)
        print(f"{2 + i}) {'핫 책 2권 나눠 쓰기' if hot else '샤드별 쓰기'}  {text}")
        print(f"   가장 바쁜 샤드 = 평균의 {ratio:.2f}배")
    board, tops = Leaderboard(4, HOT), {}
    for t, b in events:
        if t >= 3600 and 60 not in tops:
            tops[60] = board.top(5, 3600)
        board.add(t, b)
    tops[90] = board.top(5, 5400)
    print("4) 최근 1시간 상위 5권   60분 시점        90분 시점")
    for r, (a, b) in enumerate(zip(tops[60], tops[90]), 1):
        print(f"   {r}위                  {a[0]} {a[1]:>6,}   {b[0]} {b[1]:>6,}")
    same = [tops[m] == exact_top(events, 5, m * 60) for m in (60, 90)]
    print(f"5) 샤드 상위 5 합치기 = 정확한 답: 60분 {'✓' if same[0] else '✗'} · 90분 {'✓' if same[1] else '✗'}")


def approx():
    events = purchases()
    exact = Counter(b for _, b in events)
    cms = CountMin(2000, 4)
    for _, b in events:
        cms.add(b)
    cells = cms.w * cms.d
    print(f"1) 같은 주문 {len(events):,}건 · 팔린 책 {len(exact):,}권")
    print(f"2) 정확한 표: 책마다 한 칸 = {len(exact):,}칸")
    print(f"   count-min: {cms.d}줄 × {cms.w:,}칸 = {cells:,}칸 ({cells / len(exact):.0%})")
    print("3) 많이 팔린 5권  정확 → 추정")
    for b, n in exact.most_common(5):
        print(f"   {b} {n:>6,} → {cms.query(b):>6,} (+{cms.query(b) - n})")
    print("4) 한 권 팔린 책 3권  정확 → 추정")
    for b in [b for b, n in exact.items() if n == 1][:3]:
        print(f"   {b} {1:>6,} → {cms.query(b):>6,} (+{cms.query(b) - 1})")
    over = [cms.query(b) - n for b, n in exact.items()]
    print(f"5) 덜 센 책 {sum(e < 0 for e in over)}권 · 가장 많이 넘게 센 값 +{max(over)}")
    print(f"   이론 한도: e ÷ {cms.w:,} × {len(events):,} ≈ {2.71828 / cms.w * len(events):.0f}")


if __name__ == "__main__":
    {"1": ranking, "2": approx}[sys.argv[1] if len(sys.argv) > 1 else "1"]()
