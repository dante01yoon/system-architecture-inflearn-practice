"""가운데 층: 주문하기. 아래 층(storage·pricing)만 부른다."""
from bookshop.pricing import quote
from bookshop.storage import Books


def place(books: Books, isbn, qty):
    if not books.take(isbn, qty):
        return {"ok": False, "isbn": isbn}
    return {"ok": True, "isbn": isbn, "total": quote([(books.price[isbn], qty)])}
