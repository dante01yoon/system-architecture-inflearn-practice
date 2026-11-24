"""재고: 바닥나면 메일 모듈을 직접 불러 관리자에게 알린다."""
from shop_tight import email

shelf = {"Clean Architecture": 3}


def reserve(book, qty):
    shelf[book] -= qty
    if shelf[book] == 0:
        email.send_admin(f"{book} 품절")


def release(book, qty):
    shelf[book] += qty
