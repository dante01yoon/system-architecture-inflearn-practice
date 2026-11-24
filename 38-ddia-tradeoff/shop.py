"""서점 주문 DB(운영용)와 그 복사본(분석용 웨어하우스). 파이썬 표준 라이브러리만."""
import random
import sqlite3
import threading
import time


def build(path, n=200_000, seed=7):
    """주문 n건을 넣은 운영 DB를 만든다."""
    db = sqlite3.connect(path)
    db.executescript("""
        DROP TABLE IF EXISTS orders;
        CREATE TABLE orders(id INTEGER PRIMARY KEY, customer TEXT,
                            book_id INT, qty INT, price INT, day INT);
    """)
    rnd = random.Random(seed)
    rows = [(f"c{rnd.randrange(50_000)}", rnd.randrange(2_000), rnd.randint(1, 3),
             rnd.choice([12_000, 18_000, 25_000]), rnd.randrange(365)) for _ in range(n)]
    db.executemany("INSERT INTO orders(customer, book_id, qty, price, day) "
                   "VALUES (?, ?, ?, ?, ?)", rows)
    db.commit()
    return db


def copy_to_warehouse(src, path):
    """ETL을 가장 단순하게: 운영 DB를 통째로 다른 파일로 복사한다."""
    dst = sqlite3.connect(path)
    src.backup(dst)
    return dst


def checkout(db, customer, book_id):
    """주문 한 건: 짧은 쓰기 트랜잭션."""
    with db:
        db.execute("INSERT INTO orders(customer, book_id, qty, price, day) "
                   "VALUES (?, ?, 1, 18000, 365)", (customer, book_id))


def report(db):
    """매출 보고서: 주문 전체를 훑어 책별로 합친다."""
    return db.execute("""SELECT book_id, SUM(qty * price) AS sales FROM orders
                         GROUP BY book_id ORDER BY sales DESC LIMIT 3""").fetchall()


def timed_checkouts(path, n=150):
    """주문을 n번 넣으며 한 번에 걸린 시간(밀리초)을 잰다."""
    db = sqlite3.connect(path, timeout=30)
    db.execute("PRAGMA synchronous=OFF")  # 디스크 대기는 빼고 잠금 대기만 보이게
    ms = []
    for i in range(n):
        t = time.perf_counter()
        checkout(db, f"new{i}", i % 2_000)
        ms.append((time.perf_counter() - t) * 1000)
        time.sleep(0.002)  # 손님 사이 간격
    db.close()
    return ms


def while_reporting(report_path, order_path, n=150):
    """report_path에서 보고서를 계속 돌리는 동안 order_path에 주문을 넣는다."""
    stop = threading.Event()

    def analyst():
        db = sqlite3.connect(report_path, timeout=30)
        while not stop.is_set():
            report(db)
        db.close()

    t = threading.Thread(target=analyst)
    t.start()
    time.sleep(0.2)
    try:
        return timed_checkouts(order_path, n)
    finally:
        stop.set()
        t.join()


def pct(ms, p):
    s = sorted(ms)
    return s[min(len(s) - 1, int(len(s) * p / 100))]
