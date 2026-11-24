"""데이터베이스 층: 표 몇 개(dict)와 읽고 쓰는 함수."""

TABLES = {
    "books": {"Clean Architecture": 32000, "Release It!": 28000},
    "coupons": {"WELCOME10": 10},
    "orders": [],
}


def select(table):
    return TABLES[table]


def insert(table, row):
    TABLES[table].append(row)
