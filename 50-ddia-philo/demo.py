"""python3 demo.py 1 = 로그 하나에서 뷰 셋, 새 뷰를 처음부터 · python3 demo.py 2 = 유일성 제약을 로그 순서로."""
import sys

from log import AuthorPopularity, DailySales, Log, Search, Stock
from unique import N, process, route

BOOKS = [("b1", "데이터 중심 애플리케이션 설계", "클레프만"), ("b2", "리팩터링", "파울러"),
         ("b3", "클린 코드", "로버트 마틴"), ("b4", "엔터프라이즈 애플리케이션 아키텍처 패턴", "파울러")]


def shop_log():
    log = Log()
    for b, title, author in BOOKS:
        log.append({"type": "BookAdded", "book": b, "title": title, "author": author})
        log.append({"type": "StockReceived", "book": b, "qty": 10})
    for b, qty, price, day in [("b1", 2, 36000, "11-13"), ("b2", 1, 35000, "11-13"), ("b4", 1, 30000, "11-14")]:
        log.append({"type": "BookSold", "book": b, "qty": qty, "price": price, "day": day})
    return log


def one():
    log = shop_log()
    print(f"1) 로그 하나: 이벤트 {len(log.events)}개 (offset 0~{len(log.events) - 1})")
    stock, search, sales = Stock().catch_up(log), Search().catch_up(log), DailySales().catch_up(log)
    print("2) 소비자 셋이 각자 끝까지 읽음")
    print(f"   재고      b1={stock.count['b1']}  b2={stock.count['b2']}  b4={stock.count['b4']}")
    print(f"   검색      '애플리케이션' → {search.index['애플리케이션']}")
    print("   일별 매출 " + " · ".join(f"{d} {w:,}원" for d, w in sales.won.items()))
    log.append({"type": "BookSold", "book": "b3", "qty": 3, "price": 33000, "day": "11-14"})
    log.append({"type": "BookSold", "book": "b2", "qty": 2, "price": 35000, "day": "11-14"})
    for v in (stock, search, sales):
        v.catch_up(log)
    print(f"3) 판매 2건 추가 → 셋 다 따라잡음: offset {stock.offset} · {search.offset} · {sales.offset}")
    print(f"   11-14 매출 {sales.won['11-14']:,}원")
    print("4) 새 뷰 '작가 인기'를 offset 0부터 다시 읽어 만듦")
    pop = AuthorPopularity().catch_up(log)
    print("   " + " · ".join(f"{name} {n}권" for name, n in sorted(pop.sold.items(), key=lambda kv: -kv[1])))
    print(f"   새 뷰 offset {pop.offset} · 다른 뷰는 손대지 않음: {stock.offset} · {search.offset} · {sales.offset}")


REQUESTS = [{"request_id": "r1", "username": "minji"}, {"request_id": "r2", "username": "junho"},
            {"request_id": "r3", "username": "minji"}, {"request_id": "r2", "username": "junho"},
            {"request_id": "r4", "username": "seoyeon"}, {"request_id": "r5", "username": "junho"}]


def two():
    print(f"1) 가입 요청 {len(REQUESTS)}개 → 아이디로 파티션 {N}개에 나눔")
    parts = route(REQUESTS)
    print("2) 파티션마다 소비자 하나가 차례대로")
    results = []
    for k, part in enumerate(parts):
        for r, verdict in process(part):
            print(f"   p{k}  {r['request_id']}  {r['username']:<8} {verdict}")
            results.append((r["request_id"], r["username"], verdict))
    again = [(r["request_id"], r["username"], v) for part in route(REQUESTS) for r, v in process(part)]
    print(f"3) 처음부터 다시 돌려도 같은 결과: {again == results}")
    print(f"4) 수락된 아이디: {sorted({u for _, u, v in results if v == '수락'})}")


if __name__ == "__main__":
    {"1": one, "2": two}[sys.argv[1] if len(sys.argv) > 1 else "1"]()
