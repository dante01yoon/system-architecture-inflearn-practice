"""재고 소비자 둘: 받은 대로 빼는 쪽과, 처리한 메시지 번호를 표에 남겨 두 번째부터는 건너뛰는 멱등 소비자."""
import sqlite3


def open_db(qty=10):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE stock (book TEXT PRIMARY KEY, qty INT)")
    db.execute("CREATE TABLE processed (msg_id TEXT PRIMARY KEY)")
    db.execute("INSERT INTO stock VALUES ('DDIA', ?)", (qty,))
    return db


def take(db, msg):
    with db:
        db.execute("UPDATE stock SET qty = qty - ? WHERE book = ?", (msg["qty"], msg["book"]))


def take_once(db, msg):
    with db:  # 번호 남기기와 재고 빼기를 한 트랜잭션으로
        if db.execute("SELECT 1 FROM processed WHERE msg_id = ?", (msg["id"],)).fetchone():
            return False
        db.execute("INSERT INTO processed VALUES (?)", (msg["id"],))
        db.execute("UPDATE stock SET qty = qty - ? WHERE book = ?", (msg["qty"], msg["book"]))
    return True


def left(db):
    return db.execute("SELECT qty FROM stock WHERE book = 'DDIA'").fetchone()[0]
