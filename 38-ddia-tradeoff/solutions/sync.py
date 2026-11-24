"""풀이: 웨어하우스에 없는 새 주문만 옮긴다(증분 ETL)."""
import sqlite3
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from shop import build, copy_to_warehouse, timed_checkouts  # noqa: E402


def sync(orders, warehouse):
    last = warehouse.execute("SELECT COALESCE(MAX(id), 0) FROM orders").fetchone()[0]
    rows = orders.execute("SELECT * FROM orders WHERE id > ?", (last,)).fetchall()
    with warehouse:
        warehouse.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)", rows)
    return len(rows)


if __name__ == "__main__":
    d = Path(tempfile.mkdtemp())
    o = build(d / "o.db", n=20_000)
    w = copy_to_warehouse(o, d / "w.db")
    timed_checkouts(d / "o.db", n=30)
    print("옮긴 새 주문", sync(o, w), "건")
    count = lambda db: db.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    assert count(o) == count(w), (count(o), count(w))
    print("운영 DB", count(o), "건 · 웨어하우스", count(w), "건")
