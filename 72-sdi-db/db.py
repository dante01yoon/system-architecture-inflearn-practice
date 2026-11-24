"""주문 20만 줄로 인덱스가 하는 일을 잰다(sqlite3, 표준 라이브러리만)."""
import random
import sqlite3
import time


def build(n=200_000, seed=7):
    """주문 표 하나: 회원 2만 명, 책 5천 권, 날짜 365일. 인덱스는 아직 없다."""
    rnd = random.Random(seed)
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE orders(id INTEGER PRIMARY KEY, user_id INT, book_id INT, day INT)")
    rows = ((i, rnd.randrange(20_000), rnd.randrange(5_000), rnd.randrange(365)) for i in range(n))
    db.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", rows)
    return db


def plan(db, sql, args=()):
    """EXPLAIN QUERY PLAN의 마지막 칸: SCAN(전부 훑기) 또는 SEARCH … USING INDEX."""
    return " / ".join(r[-1] for r in db.execute("EXPLAIN QUERY PLAN " + sql, args))


def work(db, sql, args=()):
    """질의 하나가 한 일: 가상 머신 명령 수(실행마다 같다)와 걸린 시간(ms, 조금씩 다르다)."""
    t = time.perf_counter()
    rows = db.execute(sql, args).fetchall()
    ms = (time.perf_counter() - t) * 1000
    steps = [0]
    db.set_progress_handler(lambda: steps.__setitem__(0, steps[0] + 1), 1)
    db.execute(sql, args).fetchall()
    db.set_progress_handler(None, 0)
    return len(rows), steps[0], ms
