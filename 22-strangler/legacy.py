"""오래된 서점 시스템. 책 정보·리뷰·주문을 함수 묶음 하나가 다 한다."""
BOOKS = {
    "9780134494166": ["Clean Architecture", 32000, 3, [5, 4, 5]],
    "9781449373320": ["Designing Data-Intensive Applications", 45000, 1, [5, 5, 4, 5]],
    "9781492034025": ["Building Microservices", 41000, 0, [4, 4]],
}


def catalog(isbn):
    title, price, stock, stars = BOOKS[isbn]
    return {"title": title, "price": price}


def reviews(isbn):
    stars = BOOKS[isbn][3]
    return {"rating": round(sum(stars) / len(stars), 1), "count": len(stars)}


def order(isbn, qty):
    row = BOOKS[isbn]
    if qty > row[2]:
        return {"ok": False, "left": row[2]}
    row[2] -= qty
    return {"ok": True, "left": row[2]}
