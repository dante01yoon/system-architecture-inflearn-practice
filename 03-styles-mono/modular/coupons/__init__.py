"""쿠폰 모듈: 쿠폰 표와 할인 계산을 이 안에 가둔다."""

_COUPONS = {"WELCOME10": 10}


def discount(code, amount):
    return amount * _COUPONS.get(code, 0) // 100
