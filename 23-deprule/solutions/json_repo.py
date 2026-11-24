"""연습 풀이: JSON 파일 저장소 어댑터. usecases.py는 한 줄도 고치지 않고, 검사기도 통과한다."""
import json
import sys
import tempfile
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import checker  # noqa: E402
from bookshop.entities import Book  # noqa: E402
from bookshop.main import BOOKS  # noqa: E402
from bookshop.usecases import OrderRequest, PlaceOrder  # noqa: E402


class JsonBooks:
    def __init__(self, books, path):
        self.path = Path(path)
        self.path.write_text(json.dumps({b.isbn: asdict(b) for b in books}))

    def get(self, isbn) -> Book:
        return Book(**json.loads(self.path.read_text())[isbn])

    def save(self, book: Book):
        rows = json.loads(self.path.read_text())
        rows[book.isbn] = asdict(book)
        self.path.write_text(json.dumps(rows))


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        place = PlaceOrder(JsonBooks(BOOKS, Path(tmp, "books.json")))
        print(place(OrderRequest("9780134494166", 2)), place(OrderRequest("9780134494166", 2)))
    print("검사기:", checker.check(ROOT) or "OK")
