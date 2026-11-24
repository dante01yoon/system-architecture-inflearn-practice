"""expand-and-contract: books.price → price_krw 이름 바꾸기를 6단계로. 단계마다 옛 앱과 새 앱이 함께 돈다."""
import sqlite3

# 앱 버전마다 (읽는 칸, 쓰는 칸들)
APPS = {"v1": ("price", ["price"]), "v2": ("price", ["price", "price_krw"]),
        "v3": ("price_krw", ["price", "price_krw"]), "v4": ("price_krw", ["price_krw"])}
STEPS = [("늘리기", "ALTER TABLE books ADD COLUMN price_krw INTEGER", ["v1"]),
         ("두 칸 쓰기", None, ["v1", "v2"]),
         ("채우기", "UPDATE books SET price_krw = price WHERE price_krw IS NULL", ["v2"]),
         ("읽기 바꾸기", None, ["v2", "v3"]),
         ("옛 칸 쓰기 멈춤", None, ["v3", "v4"]),
         ("줄이기", "ALTER TABLE books DROP COLUMN price", ["v4"])]


def shop():
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT, price INTEGER)")
    db.executemany("INSERT INTO books (title, price) VALUES (?, ?)",
                   [("Clean Architecture", 32000), ("DDIA", 45000), ("Building Microservices", 38000)])
    return db, {1: 32000, 2: 45000, 3: 38000}


def work(db, truth, app, k):
    """앱 하나가 책 한 권 값을 바꾸고, 책 목록 전체를 읽는다. (오류 수, 어긋남 수)"""
    read, writes = APPS[app]
    try:
        book, price = k % 3 + 1, 30000 + k * 100
        sets = ", ".join(f"{c} = ?" for c in writes)
        db.execute(f"UPDATE books SET {sets} WHERE id = ?", [price] * len(writes) + [book])
        truth[book] = price
        rows = db.execute(f"SELECT id, {read} FROM books").fetchall()
        return 0, int(any(got != truth[i] for i, got in rows))
    except sqlite3.OperationalError:
        return 1, 0


def run(db, truth, steps=STEPS, rounds=50):
    """단계마다 (이름, 돌아가는 앱, 오류, 어긋남)."""
    rows, k = [], 0
    for name, sql, apps in steps:
        if sql:
            db.execute(sql)
        errs = bad = 0
        for _ in range(rounds):
            for app in apps:
                e, b = work(db, truth, app, k); k += 1
                errs += e; bad += b
        rows.append((name, apps, errs, bad))
    return rows
