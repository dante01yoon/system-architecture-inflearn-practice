"""서점 책 한 권(도메인 주도 설계)의 재고를 이벤트 소싱으로 다룬다."""
from store import Conflict, EventStore
from stock import load, rebuild, sales_by_day, upcast

BOOK = "book-ddd"
WEEK = "월화수목금토일"
HISTORY = [  # (날짜, 이벤트, 내용, 스키마)
    ("2026-11-09", "StockReceived", {"qty": 10}, 2),
    ("2026-11-09", "BookSold", {"count": 2}, 1),  # 예전 코드가 남긴 옛 모양(스키마 1)
    ("2026-11-10", "BookSold", {"qty": 3, "order": "o-31"}, 2),
    ("2026-11-10", "BookReturned", {"qty": 1}, 2),
    ("2026-11-11", "BookSold", {"qty": 4, "order": "o-48"}, 2),
    ("2026-11-12", "StockReceived", {"qty": 5}, 2),
    ("2026-11-13", "BookSold", {"qty": 2, "order": "o-52"}, 2),
]
SNAP_EVERY = 3


def day(d):
    return f"{d[5:]}({WEEK[(int(d[8:]) - 9) % 7]})"  # 2026-11-09가 월요일


def main():
    store = EventStore()
    print("1) 이벤트 붙이기 (지우거나 고치지 않음)")
    v = 0
    for d, type, data, schema in HISTORY:
        v = store.append(BOOK, v, type, data, d, schema)
        print(f"   v{v} {day(d)} {type:<13} {data}" + ("  ← 옛 모양(스키마 1)" if schema == 1 else ""))
        if v % SNAP_EVERY == 0:
            store.save_snapshot(BOOK, v, rebuild(store.read(BOOK)))
    print("2) 처음부터 다시 적용:", rebuild(store.read(BOOK)))
    state, snap_v, n = load(store, BOOK)
    print(f"3) 스냅숏 v{snap_v}에서 시작, 이벤트 {n}개만 적용:", state)
    tue = rebuild(store.read(BOOK, until_day="2026-11-10"))
    print(f"4) 화요일 장 마감 때 재고는? {tue['stock']}권")
    sales = sales_by_day(store.read(BOOK))
    print("5) 프로젝션 · 날짜별 판매:", " ".join(f"{day(d)} {n}권" for d, n in sales.items()))
    _, type, schema, data, _ = store.read(BOOK)[1]
    print(f"6) 업캐스터: 저장된 스키마 1 {data} → 읽을 때 스키마 2 {upcast(type, schema, data)}")
    print("7) 두 점원이 같은 v7을 읽고 동시에 판매 기록")
    store.append(BOOK, 7, "BookSold", {"qty": 1, "order": "o-60"}, "2026-11-14")
    print("   점원 A: v8 저장")
    try:
        store.append(BOOK, 7, "BookSold", {"qty": 1, "order": "o-61"}, "2026-11-14")
    except Conflict as e:
        print(f"   점원 B: 거절 ({e}) → 다시 읽고 다시 시도")


if __name__ == "__main__":
    main()
