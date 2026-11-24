"""python3 demo.py 1 → 50명이 좌석 10개에 동시에(방법 네 가지),  2 → 선점 · 만료 · 늦은 결제 · 두 번 누르기"""
import os
import sys
import tempfile

from seat import Clock, buy_locked, buy_naive, buy_unique, buy_version, connect, hold, open_event, pay, race, sweep, view


def one():
    path = os.path.join(tempfile.mkdtemp(), "seat.db")
    print("50명이 사인회 좌석 10개에 동시에 · 좌석마다 5명")
    for i, (name, buy) in enumerate([("확인하고 쓰기", buy_naive), ("비관적 잠금", buy_locked),
                                     ("낙관적 버전", buy_version), ("UNIQUE 제약", buy_unique)], 1):
        n, dup, res = race(path, buy)
        print(f"{i}. {name}")
        print(f"   표 {n}장 · 중복 {dup}장 · " + " · ".join(f"{k} {v}" for k, v in res.items()))


def two():
    path = os.path.join(tempfile.mkdtemp(), "seat.db")
    db, clock = open_event(path, ["B-7", "B-8", "B-9", "C-1"], unique=True), Clock()
    v1 = hold(db, "민지", "B-7", clock.now)
    print(f"1. 0초 민지가 B-7 선점 (5분) → 선점 번호 {v1}")
    clock.now = 10
    print(f"2. 10초 준호가 B-7 시도 → {'성공' if hold(db, '준호', 'B-7', clock.now) else '실패: 선점 중'}")
    for s, who in (("B-8", "손님a"), ("B-9", "손님b"), ("C-1", "손님c")):
        hold(db, who, s, clock.now)
    clock.now = 310
    print(f"3. 310초 민지는 결제 안 함 → 좌석 화면: B-7 {view(db, 'B-7', clock.now)}")
    v2 = hold(db, "준호", "B-7", clock.now)
    print(f"4. 310초 준호가 B-7 선점 → 선점 번호 {v2}")
    clock.now = 320
    print(f"5. 320초 민지가 늦게 결제 (번호 {v1}) → {pay(db, '민지', 'B-7', v1, clock.now, 'pay-minji')}")
    clock.now = 330
    print(f"6. 330초 준호 결제 (번호 {v2}) → {pay(db, '준호', 'B-7', v2, clock.now, 'pay-junho')}")
    print(f"7. 준호가 결제를 한 번 더 누름 → {pay(db, '준호', 'B-7', v2, clock.now, 'pay-junho')}")
    clock.now = 400
    print(f"8. 400초 청소 작업 → 만료된 선점 {sweep(db, clock.now)}개를 빈 좌석으로")
    n = db.execute("SELECT COUNT(*) FROM tickets WHERE seat_id='B-7'").fetchone()[0]
    owner = db.execute("SELECT holder FROM seats WHERE seat_id='B-7'").fetchone()[0]
    print(f"   B-7 표 {n}장 · 주인 {owner}")


if __name__ == "__main__":
    {"1": one, "2": two}[sys.argv[1] if len(sys.argv) > 1 else "1"]()
