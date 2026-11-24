"""배송 컨텍스트: 상자에 넣고 무게를 재는 책. 제목도 값도 모른다."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Parcel:
    isbn: str
    weight_g: int
    qty: int


WEIGHT_G = {"9780134494166": 680, "9781680502398": 520}
