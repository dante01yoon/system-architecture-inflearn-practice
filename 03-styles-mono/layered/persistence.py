"""퍼시스턴스 층: 데이터베이스 층만 부른다."""
from layered import database


def all_titles():
    return sorted(database.select("books"))


def price_of(title):
    return database.select("books")[title]


def coupon_rate(code):
    return database.select("coupons").get(code, 0)


def save_order(row):
    database.insert("orders", row)
