"""연습 문제 풀이: 네 번째 입구 — 밤마다 도는 배치 스크립트(CSV 주문 파일). 육각형 안쪽은 한 줄도 고치지 않는다."""
import csv
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from adapters.fakes import FakePayment, InMemoryBooks, ListNotifier  # noqa: E402
from shop.core import BookShop  # noqa: E402
from shop.ports import Book, OrderService  # noqa: E402


def run_batch(lines, service: OrderService):
    """주도하는 어댑터 ③: CSV 한 줄 = 주문 한 건."""
    done = 0
    for row in csv.DictReader(lines):
        r = service.place_order(row["isbn"], int(row["qty"]), row["card"])
        print(f"   {row['isbn']} × {row['qty']}: {r.message} · 남은 재고 {r.left}")
        done += r.ok
    return done


if __name__ == "__main__":
    shop = BookShop(InMemoryBooks(Book("B1", "Clean Architecture", 32000, 3)), FakePayment(), ListNotifier())
    orders = io.StringIO("isbn,qty,card\nB1,1,4111\nB1,1,4111\nB1,5,4111\n")
    print(f"성공 {run_batch(orders, shop)}건")
