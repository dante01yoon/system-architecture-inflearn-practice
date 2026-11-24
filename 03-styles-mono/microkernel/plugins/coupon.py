"""쿠폰 플러그인: 코어는 이 파일을 모른다. plugins 폴더에 넣으면 붙는다."""
from microkernel.core import register

COUPONS = {"WELCOME10": 10}


@register
def coupon(req, amount):
    return amount - amount * COUPONS.get(req.get("coupon", ""), 0) // 100
