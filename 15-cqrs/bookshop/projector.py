"""프로젝터: 쓰기 DB에 쌓인 이벤트를 읽어, 읽기 DB를 화면 모양으로 채운다."""

import sqlite3


def project(write_db: sqlite3.Connection, read_db: sqlite3.Connection) -> int:
    (last,) = read_db.execute("SELECT last_event_id FROM cursor").fetchone()
    events = write_db.execute(
        "SELECT id, order_id FROM events WHERE id > ? ORDER BY id", (last,)
    ).fetchall()

    for event_id, order_id in events:
        (customer,) = write_db.execute(
            "SELECT customer FROM orders WHERE id = ?", (order_id,)
        ).fetchone()
        items = write_db.execute(
            "SELECT title, qty FROM order_items WHERE order_id = ? ORDER BY rowid",
            (order_id,),
        ).fetchall()
        first_title = items[0][0]
        others = f" 외 {len(items) - 1}종" if len(items) > 1 else ""
        summary = f"{first_title}{others} · 모두 {sum(qty for _, qty in items)}권"

        with read_db:  # 같은 이벤트가 두 번 와도 결과가 같다(REPLACE)
            read_db.execute(
                "INSERT OR REPLACE INTO my_orders VALUES (?, ?, ?)",
                (order_id, customer, summary),
            )
            read_db.execute("UPDATE cursor SET last_event_id = ?", (event_id,))

    return len(events)
