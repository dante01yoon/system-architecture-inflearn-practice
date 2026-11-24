"""가장 아래 층: 금액 계산. 세 권 이상이면 10% 할인."""


def quote(items):
    """items = [(가격, 권수)] → 금액(원)."""
    total = sum(price * qty for price, qty in items)
    count = sum(qty for _, qty in items)
    return total * 9 // 10 if count >= 3 else total
