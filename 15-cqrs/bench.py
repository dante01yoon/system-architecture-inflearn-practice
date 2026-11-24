"""같은 화면(내 주문 목록)을 두 가지로 꺼내 걸린 시간을 잰다: 쓰기 DB에서 JOIN으로 / 읽기 DB에서 그대로."""

import random
import time

from bookshop.commands import PlaceOrder, handle_place_order
from bookshop.projector import project
from bookshop.queries import get_my_orders
from bookshop.schema import READ_SCHEMA, WRITE_SCHEMA, open_db

TITLES = ["Clean Architecture", "Release It!", "Building Microservices"]
ORDERS, CUSTOMERS, RUNS = 200_000, 2_000, 200

JOIN_SQL = """
SELECT o.id, MIN(i.title), COUNT(*), SUM(i.qty)
FROM orders o JOIN order_items i ON i.order_id = o.id
WHERE o.customer = ? GROUP BY o.id ORDER BY o.id DESC LIMIT 20
"""


def timed(fn) -> float:
    start = time.perf_counter()
    for n in range(RUNS):
        fn(f"c{n}")
    return (time.perf_counter() - start) / RUNS * 1000


def main() -> None:
    random.seed(1)
    write_db = open_db(":memory:", WRITE_SCHEMA)
    read_db = open_db(":memory:", READ_SCHEMA)
    write_db.executemany(
        "INSERT INTO books VALUES (?, ?)", [(t, 10**9) for t in TITLES]
    )
    for _ in range(ORDERS):
        items = {
            t: random.randint(1, 3) for t in random.sample(TITLES, random.randint(1, 3))
        }
        handle_place_order(
            write_db, PlaceOrder(f"c{random.randrange(CUSTOMERS)}", items)
        )
    project(write_db, read_db)

    print(f"주문 {ORDERS:,}건, 고객 {CUSTOMERS:,}명 · 내 주문 목록 화면 한 번")
    print(
        f"   쓰기 DB에서 JOIN으로  {timed(lambda c: write_db.execute(JOIN_SQL, (c,)).fetchall()):8.3f} ms"
    )
    print(
        f"   읽기 DB에서 그대로    {timed(lambda c: get_my_orders(read_db, c)):8.3f} ms"
    )


if __name__ == "__main__":
    main()
