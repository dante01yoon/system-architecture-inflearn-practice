"""새로 만드는 서비스. 레거시의 일을 하나씩 옮겨 온다(지금은 카탈로그와 리뷰)."""
from dataclasses import dataclass


@dataclass
class Book:
    title: str
    price: int


CATALOG = {
    "9780134494166": Book("Clean Architecture", 32000),
    "9781449373320": Book("Designing Data-Intensive Applications", 45000),
    "9781492034025": Book("Building Microservices", 41000),
}
STARS = {"9780134494166": [5, 4, 5], "9781449373320": [5, 5, 4, 5], "9781492034025": [4, 4]}


def catalog(isbn):
    book = CATALOG[isbn]
    return {"title": book.title, "price": book.price}


def reviews(isbn):
    stars = STARS[isbn]
    return {"rating": round(sum(stars) / len(stars), 1), "count": len(stars)}
