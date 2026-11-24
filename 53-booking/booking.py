"""선착순 예약 모형: 300석, 10시 정각부터 10초 동안 30,000명(seed 고정). 숫자는 모두 가정한 값이다."""
import os
import random
import sqlite3
import tempfile
import threading

SEATS, PEOPLE, SECONDS, WORKERS = 300, 30_000, 10, 3


def arrivals(seed=7):
    """도착 시각(초). 가정: 정각 직후에 가장 몰리고 점점 줄어든다(평균 1초 지수 분포, 10초 안)."""
    rng, out = random.Random(seed), []
    while len(out) < PEOPLE:
        t = rng.expovariate(1.0)
        if t < SECONDS:
            out.append(t)
    return sorted(out)


def open_db(seats=SEATS):
    path = os.path.join(tempfile.mkdtemp(), "booking.db")
    db = sqlite3.connect(path)
    db.executescript("PRAGMA journal_mode=WAL; PRAGMA synchronous=OFF;"
                     "CREATE TABLE stock(id INTEGER PRIMARY KEY, left INTEGER);"
                     "CREATE TABLE reservation(person INTEGER, key TEXT UNIQUE);")
    db.execute("INSERT INTO stock VALUES (1, ?)", (seats,))
    db.commit(); db.close()
    return path


def connect(path):
    return sqlite3.connect(path, timeout=30, isolation_level=None, check_same_thread=False)


# ── (1) 읽고, 확인하고, 쓰기 — 세 번 따로 보낸다 ──
def naive_read(db):
    return db.execute("SELECT left FROM stock WHERE id = 1").fetchone()[0]


def naive_write(db, person, left):
    if left <= 0:
        return False                                   # 매진
    db.execute("UPDATE stock SET left = ? WHERE id = 1", (left - 1,))
    db.execute("INSERT INTO reservation(person) VALUES (?)", (person,))
    return True


# ── (2) 조건부 UPDATE 한 문장 — 남았을 때만 하나 뺀다 ──
def atomic_reserve(db, person, key=None):
    db.execute("BEGIN IMMEDIATE")
    try:
        if key and db.execute("SELECT 1 FROM reservation WHERE key = ?", (key,)).fetchone():
            db.execute("COMMIT")
            return True                                # 같은 키 = 이미 처리한 요청
        n = db.execute("UPDATE stock SET left = left - 1 WHERE id = 1 AND left > 0").rowcount
        if n == 1:
            db.execute("INSERT INTO reservation(person, key) VALUES (?, ?)", (person, key))
        db.execute("COMMIT")
        return n == 1
    except Exception:
        db.execute("ROLLBACK")
        raise


def run_threads(path, times, gap_ms, read, write):
    """도착 시각을 gap_ms 칸으로 묶는다. 같은 칸의 요청은 스레드 WORKERS개가 나눠 「모두 읽은 뒤 모두 쓴다」
    — 가정: 읽고 나서 쓰기까지 gap_ms 걸려서, 같은 칸끼리는 서로의 쓰기를 못 본다."""
    waves = {}
    for person, t in enumerate(times):
        waves.setdefault(int(t * 1000 // gap_ms), []).append(person)
    order = [waves[k] for k in sorted(waves)]
    barrier, won = threading.Barrier(WORKERS), [0] * WORKERS

    def worker(w):
        db = connect(path)
        for wave in order:
            mine = wave[w::WORKERS]
            seen = [read(db) for _ in mine] if read else [None] * len(mine)
            barrier.wait()                             # 이 칸의 읽기가 다 끝난 뒤
            won[w] += sum(write(db, p, s) for p, s in zip(mine, seen))
            barrier.wait()                             # 이 칸의 쓰기가 다 끝난 뒤 다음 칸
        db.close()
    ts = [threading.Thread(target=worker, args=(w,)) for w in range(WORKERS)]
    [t.start() for t in ts]; [t.join() for t in ts]
    return sum(won)


def sold(path):
    db = connect(path)
    n = db.execute("SELECT COUNT(*) FROM reservation").fetchone()[0]
    left = db.execute("SELECT left FROM stock").fetchone()[0]
    db.close()
    return n, left


def peak_per_second(times):
    per = [0] * SECONDS
    for t in times:
        per[int(t)] += 1
    return max(per)


# ── (3) 대기실: 도착 순서대로 번호표, 1초에 rate명만 들여보낸다 ──
def waiting_room(times, rate, seats=SEATS):
    """들어간 사람만 데이터베이스에 간다. 좌석이 끝나면 남은 줄 전체에 한 번에 매진을 알린다."""
    path = open_db(seats)
    db = connect(path)
    admitted, waits, sold_out_at = 0, [], None
    for person, t in enumerate(times):                # times는 도착 순 = 번호표 순(공정함)
        slot = admitted / rate                         # 이 사람이 들어갈 수 있는 가장 이른 시각
        enter = max(t, slot)
        if sold_out_at is not None and enter >= sold_out_at:
            break
        admitted += 1
        if atomic_reserve(db, person):
            waits.append(enter - t)
            if sold(path)[0] == seats:
                sold_out_at = enter
    db.close()
    return sold(path), admitted, waits


def pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(len(xs) * p / 100))]
