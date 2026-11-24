"""쓰기 쪽: 커맨드(Command)를 받아 규칙을 확인하고 상태를 바꾼다. 값을 돌려주지 않는다."""

import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class PlaceOrder:
    customer: str
    items: dict[str, int]  # 책 제목 -> 권수


class OutOfStock(Exception):
    pass


def handle_place_order(db: sqlite3.Connection, cmd: PlaceOrder) -> None:
    with db:  # 한 트랜잭션: 전부 저장되거나, 전부 취소되거나
        for title, qty in cmd.items.items():
            (stock,) = db.execute(
                "SELECT stock FROM books WHERE title = ?", (title,)
            ).fetchone()
            if stock < qty:
                raise OutOfStock(f"{title}: 재고 {stock}권, 주문 {qty}권")
            db.execute(
                "UPDATE books SET stock = stock - ? WHERE title = ?", (qty, title)
            )

        order_id = db.execute(
            "INSERT INTO orders (customer) VALUES (?)", (cmd.customer,)
        ).lastrowid
        db.executemany(
            "INSERT INTO order_items VALUES (?, ?, ?)",
            [(order_id, title, qty) for title, qty in cmd.items.items()],
        )
        db.execute(
            "INSERT INTO events (kind, order_id) VALUES ('OrderPlaced', ?)", (order_id,)
        )
