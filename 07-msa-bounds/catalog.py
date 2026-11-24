"""카탈로그 컨텍스트: 책을 고르는 사람에게 보여 줄 책."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Book:
    isbn: str
    title: str
    author: str
    price: int
    blurb: str


SHELF = {
    "9780134494166": Book("9780134494166", "Clean Architecture", "Robert C. Martin", 32000, "의존성 규칙과 경계"),
    "9781680502398": Book("9781680502398", "Release It!", "Michael T. Nygard", 30000, "운영에서 살아남는 설계"),
}
