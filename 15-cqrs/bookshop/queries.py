"""읽기 쪽: 쿼리(Query)는 읽기 DB에서 화면 모양 그대로 꺼낸다. 아무것도 바꾸지 않는다."""

import sqlite3


def get_my_orders(read_db: sqlite3.Connection, customer: str) -> list[tuple[int, str]]:
    return read_db.execute(
        "SELECT order_id, summary FROM my_orders WHERE customer = ? "
        "ORDER BY order_id DESC LIMIT 20",
        (customer,),
    ).fetchall()
