"""연습 문제 풀이: '책별 판매 권수' 읽기 모델을 하나 더 붙인다. 쓰기 쪽(commands.py)은 고치지 않는다.

실행: python3 -m solutions.best_sellers
"""

import sqlite3

from bookshop.commands import PlaceOrder, handle_place_order
from bookshop.schema import WRITE_SCHEMA, open_db

READ_SCHEMA = """
CREATE TABLE best_sellers (title TEXT PRIMARY KEY, sold INTEGER NOT NULL);
CREATE TABLE cursor (last_event_id INTEGER NOT NULL);
INSERT INTO cursor VALUES (0);
"""


def project(write_db: sqlite3.Connection, read_db: sqlite3.Connection) -> int:
    (last,) = read_db.execute("SELECT last_event_id FROM cursor").fetchone()
    events = write_db.execute(
        "SELECT id, order_id FROM events WHERE id > ? ORDER BY id", (last,)
    ).fetchall()
    for event_id, order_id in events:
        items = write_db.execute(
            "SELECT title, qty FROM order_items WHERE order_id = ?", (order_id,)
        ).fetchall()
        with (
            read_db
        ):  # 더하기는 REPLACE와 달리 두 번 하면 틀린다 -> 책갈피와 한 트랜잭션으로
            read_db.executemany(
                "INSERT INTO best_sellers VALUES (?, ?) "
                "ON CONFLICT (title) DO UPDATE SET sold = sold + excluded.sold",
                items,
            )
            read_db.execute("UPDATE cursor SET last_event_id = ?", (event_id,))
    return len(events)


def get_best_sellers(read_db: sqlite3.Connection) -> list[tuple[str, int]]:
    return read_db.execute(
        "SELECT title, sold FROM best_sellers ORDER BY sold DESC, title"
    ).fetchall()


if __name__ == "__main__":
    w, r = open_db(":memory:", WRITE_SCHEMA), open_db(":memory:", READ_SCHEMA)
    w.executemany(
        "INSERT INTO books VALUES (?, 9)", [("Clean Architecture",), ("Release It!",)]
    )
    handle_place_order(
        w, PlaceOrder("dante", {"Clean Architecture": 2, "Release It!": 1})
    )
    handle_place_order(w, PlaceOrder("dante", {"Release It!": 3}))
    assert project(w, r) == 2 and project(w, r) == 0
    assert get_best_sellers(r) == [("Release It!", 4), ("Clean Architecture", 2)]
    print(get_best_sellers(r))
