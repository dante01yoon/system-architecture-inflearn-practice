"""비즈니스 층: 규칙을 둔다. 퍼시스턴스 층만 부른다."""
from layered import persistence


def list_books():
    return persistence.all_titles()


def place_order(req):
    amount = persistence.price_of(req["title"]) * req["qty"]
    amount -= amount * persistence.coupon_rate(req.get("coupon", "")) // 100
    persistence.save_order((req["title"], req["qty"], amount))
    return amount
