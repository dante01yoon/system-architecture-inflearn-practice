"""서점의 네 단계(주문 → 결제 → 재고 → 배송)와 각 단계의 보상. 모두 sqlite3 한 파일."""
import sqlite3


def open_db(path):
    db = sqlite3.connect(path, timeout=0.2)
    db.executescript("""
        CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY, book TEXT, qty INT, status TEXT);
        CREATE TABLE IF NOT EXISTS payments(order_id INT, amount INT, status TEXT);
        CREATE TABLE IF NOT EXISTS stock(book TEXT PRIMARY KEY, qty INT);
        CREATE TABLE IF NOT EXISTS shipments(order_id INT);""")
    return db


def create_order(db, o):     # T1
    db.execute("INSERT INTO orders VALUES (?, ?, ?, 'PENDING')", (o["id"], o["book"], o["qty"]))


def cancel_order(db, o):     # C1: 지우지 않고 취소로 바꾼다
    db.execute("UPDATE orders SET status = 'CANCELLED' WHERE id = ?", (o["id"],))


def charge(db, o):           # T2
    db.execute("INSERT INTO payments VALUES (?, ?, 'PAID')", (o["id"], o["price"]))


def refund(db, o):           # C2: 결제 기록은 남기고 환불로
    db.execute("UPDATE payments SET status = 'REFUNDED' WHERE order_id = ?", (o["id"],))


def reserve(db, o):          # T3
    left = db.execute("SELECT qty FROM stock WHERE book = ?", (o["book"],)).fetchone()[0]
    if left < o["qty"]:
        raise ValueError(f"재고 {left}권")
    db.execute("UPDATE stock SET qty = qty - ? WHERE book = ?", (o["qty"], o["book"]))


def release(db, o):          # C3: 그때 값으로 덮지 않고 그만큼 더한다
    db.execute("UPDATE stock SET qty = qty + ? WHERE book = ?", (o["qty"], o["book"]))


def ship(db, o):             # T4: 배송을 맡기고 주문 확정
    db.execute("INSERT INTO shipments VALUES (?)", (o["id"],))
    db.execute("UPDATE orders SET status = 'SHIPPED' WHERE id = ?", (o["id"],))


def nothing(db, o):          # 마지막 단계는 보상할 일이 없다
    pass


STEPS = [("주문", create_order, cancel_order), ("결제", charge, refund),
         ("재고", reserve, release), ("배송", ship, nothing)]
