"""저장소 두 개: 쓰기 DB(규칙을 지키는 원본)와 읽기 DB(화면 모양 그대로)."""

import sqlite3

WRITE_SCHEMA = """
CREATE TABLE books (title TEXT PRIMARY KEY, stock INTEGER NOT NULL CHECK (stock >= 0));
CREATE TABLE orders (id INTEGER PRIMARY KEY, customer TEXT NOT NULL);
CREATE TABLE order_items (
    order_id INTEGER NOT NULL REFERENCES orders (id),
    title TEXT NOT NULL REFERENCES books (title),
    qty INTEGER NOT NULL CHECK (qty > 0)
);
CREATE INDEX orders_customer ON orders (customer);
CREATE INDEX order_items_order ON order_items (order_id);
CREATE TABLE events (id INTEGER PRIMARY KEY, kind TEXT NOT NULL, order_id INTEGER NOT NULL);
"""

READ_SCHEMA = """
CREATE TABLE my_orders (
    order_id INTEGER PRIMARY KEY,
    customer TEXT NOT NULL,
    summary TEXT NOT NULL
);
CREATE INDEX my_orders_customer ON my_orders (customer);
CREATE TABLE cursor (last_event_id INTEGER NOT NULL);
INSERT INTO cursor VALUES (0);
"""


def open_db(path: str, schema: str) -> sqlite3.Connection:
    db = sqlite3.connect(path)
    db.executescript(schema)
    return db
