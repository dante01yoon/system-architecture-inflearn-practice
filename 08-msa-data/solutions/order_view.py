"""연습 풀이: 「주문 번호 · 책 제목 · 남은 재고」 화면을 API 조합(API Composition)으로 만든다.
주문 서비스와 재고 서비스에 각각 묻고, 합치는 일은 바깥(여기)에서 한다. 남의 DB 파일을 열지 않는다."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from order import OrderService  # noqa: E402
from stock import StockService  # noqa: E402

TITLES = {"9780134494166": "Clean Architecture"}  # 카탈로그 서비스가 답했다고 치는 값


def order_view(orders, stock):
    rows = orders.db.execute("SELECT id, isbn, qty, status FROM orders ORDER BY id").fetchall()  # 주문 서비스의 답
    return [(oid, TITLES[isbn], qty, status, stock.left(isbn)) for oid, isbn, qty, status in rows]  # 재고 서비스의 답과 합침


d = Path(tempfile.mkdtemp())
s, o = StockService(d / "stock.db"), OrderService(d / "orders.db")
with s.db:
    s.db.execute("INSERT INTO stock VALUES ('9780134494166', 5)")
o.place_sync(s, "9780134494166", 2)
view = order_view(o, s)
assert view == [(1, "Clean Architecture", 2, "확정", 3)], view
print(view)
