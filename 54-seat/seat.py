"""작가 사인회 좌석: 동시에 사기 · 선점(hold)과 만료 · 결제 확정. sqlite3 파일 하나."""
import sqlite3
import threading
import time

THINK = 0.1   # 읽고 나서 쓰기까지 걸리는 시간(네트워크 왕복 흉내) — 이 틈에 경쟁이 생긴다


def connect(path):
    db = sqlite3.connect(path, timeout=30, isolation_level=None, check_same_thread=False)
    db.execute("PRAGMA journal_mode=WAL")      # 읽는 쪽이 쓰는 쪽을 기다리지 않게
    return db


def open_event(path, seats, unique):
    db = connect(path)
    db.executescript("DROP TABLE IF EXISTS seats; DROP TABLE IF EXISTS tickets;"
                     "DROP TABLE IF EXISTS pay_keys;")
    db.execute("CREATE TABLE seats(seat_id TEXT PRIMARY KEY, status TEXT, holder TEXT,"
               " expires_at INTEGER, version INTEGER)")
    guard = ", UNIQUE(event_id, seat_id)" if unique else ""
    db.execute(f"CREATE TABLE tickets(event_id TEXT, seat_id TEXT, buyer TEXT{guard})")
    db.execute("CREATE TABLE pay_keys(key TEXT PRIMARY KEY, result TEXT)")
    db.executemany("INSERT INTO seats VALUES(?, 'free', NULL, 0, 0)", [(s,) for s in seats])
    return db


def status(db, seat):
    return db.execute("SELECT status, version FROM seats WHERE seat_id=?", (seat,)).fetchone()


# ── 1. 동시에 사기: 방법 네 가지 ──
def buy_naive(db, who, seat):
    free = status(db, seat)[0] == "free"
    time.sleep(THINK)
    if not free:
        return "매진"
    db.execute("INSERT INTO tickets VALUES('sign-1', ?, ?)", (seat, who))
    db.execute("UPDATE seats SET status='sold', holder=? WHERE seat_id=?", (who, seat))
    return "구매"


def buy_locked(db, who, seat):
    db.execute("BEGIN IMMEDIATE")      # 비관적: 처음부터 잠금
    try:
        return buy_naive(db, who, seat)
    finally:
        db.execute("COMMIT")


def buy_version(db, who, seat):
    st, ver = status(db, seat)
    time.sleep(THINK)
    if st != "free":
        return "매진"
    won = db.execute("UPDATE seats SET status='sold', holder=?, version=version+1"
                     " WHERE seat_id=? AND version=?", (who, seat, ver)).rowcount
    if not won:
        return "충돌"   # 낙관적: 버전이 바뀜
    db.execute("INSERT INTO tickets VALUES('sign-1', ?, ?)", (seat, who))
    return "구매"


def buy_unique(db, who, seat):
    try:
        return buy_naive(db, who, seat)
    except sqlite3.IntegrityError:
        return "거절"   # 마지막 방어선


def race(path, buy, people=50, seats=10):
    """people명이 seats개 좌석에 동시에(좌석마다 people/seats명). → (표, 중복 표, 결과별 수)"""
    names = [f"S-{k + 1}" for k in range(seats)]
    open_event(path, names, unique=buy is buy_unique).close()
    gate, out = threading.Barrier(people), []

    def one(i):
        db = connect(path)
        gate.wait()
        out.append(buy(db, f"손님{i}", names[i % seats]))
        db.close()

    ts = [threading.Thread(target=one, args=(i,)) for i in range(people)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    db = connect(path)
    n = db.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
    dup = n - db.execute("SELECT COUNT(DISTINCT seat_id) FROM tickets").fetchone()[0]
    return n, dup, {k: out.count(k) for k in ("구매", "매진", "충돌", "거절") if k in out}


# ── 2. 선점과 만료 ──
class Clock:
    """시연용 시계(초). 실제로는 DB 서버 한 곳의 시각을 쓴다."""
    def __init__(self, now=0):
        self.now = now


def hold(db, who, seat, now, ttl=300):
    """빈 좌석이나 만료된 선점만 잡는다(쓸 때 만료 판정). 성공하면 선점 번호."""
    cur = db.execute("UPDATE seats SET status='held', holder=?, expires_at=?,"
                     " version=version+1 WHERE seat_id=? AND (status='free'"
                     " OR (status='held' AND expires_at<=?))", (who, now + ttl, seat, now))
    if not cur.rowcount:
        return None
    return status(db, seat)[1]


def view(db, seat, now):
    """손님 화면: 만료된 선점은 줄이 남아 있어도 빈 좌석으로 보인다(lazy)."""
    st, exp = db.execute("SELECT status, expires_at FROM seats WHERE seat_id=?",
                         (seat,)).fetchone()
    if st == "free" or (st == "held" and exp <= now):
        return "빈 좌석"
    return {"held": "선점 중", "sold": "판매 완료"}[st]


def pay(db, who, seat, ver, now, key):
    """선점 번호가 그대로이고 만료 전일 때만 확정. 같은 key면 처음 결과."""
    old = db.execute("SELECT result FROM pay_keys WHERE key=?", (key,)).fetchone()
    if old:
        return old[0] + " (같은 키 · 처음 결과)"
    db.execute("BEGIN IMMEDIATE")
    ok = db.execute("UPDATE seats SET status='sold' WHERE seat_id=? AND status='held'"
                    " AND holder=? AND version=? AND expires_at>?",
                    (seat, who, ver, now)).rowcount
    if ok:
        db.execute("INSERT INTO tickets VALUES('sign-1', ?, ?)", (seat, who))
    result = "확정" if ok else f"거절: 지금 선점 번호 {status(db, seat)[1]}"
    db.execute("INSERT INTO pay_keys VALUES(?, ?)", (key, result))
    db.execute("COMMIT")
    return result


def sweep(db, now):
    """청소 작업(sweeper): 만료된 선점을 빈 좌석으로 되돌린다. 되돌린 수."""
    return db.execute("UPDATE seats SET status='free', holder=NULL"
                      " WHERE status='held' AND expires_at<=?", (now,)).rowcount
