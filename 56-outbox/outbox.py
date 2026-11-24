"""Transactional Outbox 예제: 주문 저장과 이벤트 발행을 함께 (파이썬 표준 라이브러리만)."""
import json
import sqlite3


class Crash(Exception):
    """서버가 그 자리에서 죽은 것처럼 멈춘다(실험용)."""


def open_db():
    db = sqlite3.connect(":memory:")
    db.executescript("""
    CREATE TABLE orders (id INTEGER PRIMARY KEY, book TEXT, status TEXT);
    CREATE TABLE outbox (seq INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id TEXT, order_id INTEGER, type TEXT, payload TEXT,
        published INTEGER DEFAULT 0);
    -- 트랜잭션 로그 흉내: 커밋된 outbox 행이 커밋 순서대로 복사된다
    CREATE TABLE txlog (seq INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id TEXT, order_id INTEGER, type TEXT, payload TEXT);
    CREATE TRIGGER tail AFTER INSERT ON outbox BEGIN
        INSERT INTO txlog (event_id, order_id, type, payload)
        VALUES (NEW.event_id, NEW.order_id, NEW.type, NEW.payload); END;
    """)
    return db


def place_naive(db, broker, order_id, book, crash=False):
    with db:
        db.execute("INSERT INTO orders VALUES (?, ?, '주문됨')", (order_id, book))
    if crash:
        raise Crash("저장 뒤, 발행 전")
    broker.append({"id": f"OrderPlaced#{order_id}", "key": order_id,
                   "type": "OrderPlaced", "book": book})


def add_event(db, order_id, type, **payload):
    # 이벤트 id = 소비자가 중복을 알아보는 번호(실서비스는 UUID)
    db.execute("INSERT INTO outbox (event_id, order_id, type, payload)"
               " VALUES (?, ?, ?, ?)", (f"{type}#{order_id}", order_id,
                                        type, json.dumps(payload)))


def place(db, order_id, book, crash=None):
    with db:  # 주문과 이벤트를 한 트랜잭션에
        db.execute("INSERT INTO orders VALUES (?, ?, '주문됨')", (order_id, book))
        if crash == "inside":
            raise Crash("커밋 전")
        add_event(db, order_id, "OrderPlaced", book=book)
    if crash == "after":
        raise Crash("커밋 뒤")


def cancel(db, order_id):
    with db:
        db.execute("UPDATE orders SET status = '취소' WHERE id = ?", (order_id,))
        book = db.execute("SELECT book FROM orders WHERE id = ?",
                          (order_id,)).fetchone()[0]
        add_event(db, order_id, "OrderCancelled", book=book)


def _send(broker, eid, oid, type, payload):
    broker.append({"id": eid, "key": oid, "type": type, **json.loads(payload)})


class PollingRelay:
    """폴링 전달자: 아직 안 보낸 행을 seq 순서로 읽어 보내고 표시한다."""

    def __init__(self, db, broker):
        self.db, self.broker = db, broker

    def run(self, crash_after_send=False):
        rows = self.db.execute(
            "SELECT seq, event_id, order_id, type, payload FROM outbox"
            " WHERE published = 0 ORDER BY seq").fetchall()
        for seq, *event in rows:
            _send(self.broker, *event)
            if crash_after_send:
                raise Crash("보낸 뒤, 표시 전")
            with self.db:
                self.db.execute("UPDATE outbox SET published = 1"
                                " WHERE seq = ?", (seq,))
        return len(rows)


class TailingRelay:
    """로그 테일링 흉내: txlog를 오프셋 뒤부터 따라 읽는다(표는 고치지 않음)."""

    def __init__(self, db, broker):
        self.db, self.broker, self.offset = db, broker, 0

    def run(self):
        rows = self.db.execute(
            "SELECT seq, event_id, order_id, type, payload FROM txlog"
            " WHERE seq > ? ORDER BY seq", (self.offset,)).fetchall()
        for seq, *event in rows:
            _send(self.broker, *event)
            self.offset = seq  # 보낸 뒤 오프셋 저장 — 그 사이에 죽으면 중복
        return len(rows)


class Consumer:
    """재고 서비스: 이벤트 id로 중복을 걸러 내는 멱등 소비자."""

    def __init__(self):
        self.seen, self.reserved = set(), {}

    def handle(self, event):
        if event["id"] in self.seen:  # 실서비스는 처리 결과와 같은 트랜잭션에 저장
            return "중복 무시"
        self.seen.add(event["id"])
        book = event["book"]
        self.reserved[book] = self.reserved.get(book, 0) + 1
        return "처리"


def cleanup(db):
    with db:
        return db.execute("DELETE FROM outbox WHERE published = 1").rowcount


def count(db, sql):
    return db.execute(sql).fetchone()[0]
