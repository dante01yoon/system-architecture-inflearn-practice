"""주문 DB와 검색 인덱스 맞추기(이중 쓰기 대 CDC), 그리고 이벤트 시각 기준 1분 창(텀블링 윈도)."""
import sqlite3

SCHEMA = """
CREATE TABLE orders (id INTEGER PRIMARY KEY, title TEXT, status TEXT);
CREATE TABLE changes (seq INTEGER PRIMARY KEY AUTOINCREMENT,
                      order_id INTEGER, status TEXT);
-- CDC 흉내: 진짜 CDC는 DB의 복제 로그(WAL·binlog)를 읽는다.
-- 여기선 트리거가 커밋 순서대로 같은 기록을 남긴다.
CREATE TRIGGER log_insert AFTER INSERT ON orders BEGIN
  INSERT INTO changes (order_id, status) VALUES (NEW.id, NEW.status);
END;
CREATE TRIGGER log_update AFTER UPDATE ON orders BEGIN
  INSERT INTO changes (order_id, status) VALUES (NEW.id, NEW.status);
END;
"""


def open_db():
    db = sqlite3.connect(":memory:")
    db.executescript(SCHEMA)
    return db


def set_status(db, order_id, status):
    with db:
        db.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))


# ── 이중 쓰기: 앱이 DB와 검색 인덱스에 따로 쓴다 ──
def dual_write(db, index, steps):
    """steps = [(요청, 'db'|'index', 상태)] — 두 요청의 쓰기가 섞이는 순서를 고정해 재현한다."""
    for who, target, status in steps:
        if target == "db":
            set_status(db, 1, status)
        else:
            index[1] = status
        yield who, target, status


# ── CDC: 앱은 DB에만 쓰고, 소비자가 변경 로그를 순서대로 따라 적는다 ──
class Consumer:
    def __init__(self, db):
        self.db, self.offset, self.view = db, 0, {}

    def poll(self):
        rows = self.db.execute("SELECT seq, order_id, status FROM changes"
                               " WHERE seq > ? ORDER BY seq", (self.offset,)).fetchall()
        for seq, order_id, status in rows:
            self.view[order_id] = status  # 덮어쓰기라 같은 변경이 두 번 와도 결과가 같다
            self.offset = seq  # 어디까지 적용했는지(오프셋)
        return rows


# ── 텀블링 윈도: 일어난 시각으로 1분씩 자르고, 늦은 이벤트를 grace초까지 기다린다 ──
def tumbling(events, size=60, grace=30):
    """events = 도착 순서의 (일어난 초, 도착 초, 금액).
    워터마크 = 지금까지 본 가장 늦은 일어난 시각."""
    open_, closed, late, mark = {}, [], [], 0
    for t, arrived, won in events:
        start = t // size * size
        if any(c[0] == start for c in closed):
            late.append((t, arrived, won))  # 이미 닫힌 창 → 따로 보관
            continue
        open_.setdefault(start, []).append(won)
        mark = max(mark, t)
        for s in sorted(open_):
            if mark >= s + size + grace:  # 창 끝 + 기다림이 지나면 닫는다
                closed.append((s, open_.pop(s), arrived))
    closed += [(s, open_.pop(s), None) for s in sorted(open_)]
    return closed, late


def by_arrival(events, size=60):
    out = {}
    for _, arrived, won in events:
        out.setdefault(arrived // size * size, []).append(won)
    return sorted(out.items())


SALES = [(5, 6, 32000), (20, 21, 35000), (41, 42, 45000), (65, 66, 38000), (72, 73, 30000),
         (50, 80, 48000), (88, 89, 33000), (110, 111, 25000), (125, 126, 31000), (58, 130, 35000),
         (140, 141, 48000), (170, 171, 45000)]


def clock(sec):
    return f"10:{sec // 60:02d}:{sec % 60:02d}"
