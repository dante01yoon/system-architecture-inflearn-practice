"""운영 DB에서 매출 보고서를 돌리면 주문이 얼마나 느려지나, 웨어하우스로 옮기면 어떻게 되나."""
import sqlite3
import tempfile
import time
import unicodedata
from pathlib import Path

from shop import build, copy_to_warehouse, pct, report, timed_checkouts, while_reporting


def line(label, ms):
    slow = sum(m > 10 for m in ms)
    label += " " * (22 - sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in label))  # 한글 폭 맞춤
    print(f"   {label}  {sum(ms) / len(ms):6.2f}ms  {pct(ms, 99):6.2f}ms  {slow:3d}건")


def main():
    d = Path(tempfile.mkdtemp())
    orders, warehouse = d / "orders.db", d / "warehouse.db"

    db = build(orders)
    print(f"1) 운영 DB orders.db: 주문 {db.execute('SELECT COUNT(*) FROM orders').fetchone()[0]:,}건")

    t = time.perf_counter()
    copy_to_warehouse(db, warehouse).close()
    print(f"2) 웨어하우스 warehouse.db로 복사(ETL): {time.perf_counter() - t:.2f}초")

    t = time.perf_counter()
    top = report(db)
    print(f"3) 매출 보고서 한 번: {(time.perf_counter() - t) * 1000:.0f}ms (주문 전체를 훑음)")
    print(f"   1위 책 #{top[0][0]}  매출 {top[0][1]:,}원")
    db.close()

    print("4) 주문 150건 넣기         평균       p99   10ms 넘음")
    line("혼자일 때", timed_checkouts(orders))
    line("같은 DB에서 보고서", while_reporting(orders, orders))
    line("웨어하우스에서 보고서", while_reporting(warehouse, orders))

    n_op = sqlite3.connect(orders).execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    n_wh = sqlite3.connect(warehouse).execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    print("5) 대가: 웨어하우스는 복사한 순간의 사진")
    print(f"   운영 DB {n_op:,}건 · 웨어하우스 {n_wh:,}건")


if __name__ == "__main__":
    main()
