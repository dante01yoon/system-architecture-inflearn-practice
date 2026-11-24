"""python3 demo.py 1 → offset 대 cursor,  2 → PUT 대 POST 재시도,  3 → 짧은 폴링 대 롱 폴링"""
import json
import sys
from urllib.request import Request, urlopen

from api import PORT, reset, serve
from poll import arrivals, long_poll, short_poll

BASE = f"http://127.0.0.1:{PORT}"


def call(method, path, body=None, headers=None):
    data = json.dumps(body).encode() if body is not None else None
    with urlopen(Request(BASE + path, data=data, method=method, headers=headers or {})) as r:
        return r.status, json.loads(r.read())


def books(path):
    items = call("GET", path)[1]
    print(f"   GET {path:<31} → {' '.join(map(str, items['items']))}"
          + (f"  next_cursor={items['next_cursor']}" if "next_cursor" in items else ""))
    return items["items"]


def new_book():
    print(f"   POST /v1/books{'':<21} → 새 책 {call('POST', '/v1/books')[1]['id']}")


def one():
    print("1) offset 페이지네이션 · 새 책 순서")
    a = books("/v1/books?offset=0&limit=5")
    new_book()
    b = books("/v1/books?offset=5&limit=5")
    print(f"   두 쪽에 같은 책: {sorted(set(a) & set(b)) or '없음'}")
    reset()
    print("2) cursor 페이지네이션 · 처음 상태로")
    a = books("/v1/books?limit=5")
    new_book()
    b = books(f"/v1/books?cursor={a[-1]}&limit=5")
    print(f"   두 쪽에 같은 책: {sorted(set(a) & set(b)) or '없음'}")


def two():
    print("1) 응답이 끊겨 같은 요청을 두 번 보냄")
    for _ in range(2):
        s, r = call("PUT", "/v1/wishlist/7")
        print(f"   PUT  /v1/wishlist/7           → {s} 위시리스트 {r['wishlist']}")
    print(f"   위시리스트에는 {len(r['wishlist'])}권만 있음")
    for _ in range(2):
        s, r = call("POST", "/v1/orders", {"book_id": 7})
        print(f"   POST /v1/orders {{book_id: 7}}  → {s} 주문 {r['order_id']}번")
    print("   같은 책 주문이 2건 생김")
    print("2) POST에 Idempotency-Key를 붙여 두 번")
    for _ in range(2):
        s, r = call("POST", "/v1/orders", {"book_id": 7}, {"Idempotency-Key": "a1"})
        print(f"   POST /v1/orders  key=a1       → {s} 주문 {r['order_id']}번")
    print("   두 번째는 처음 답을 그대로 돌려줌")


def three():
    hour, times = 3600, arrivals(12, 3600)
    print(f"1) 한 시간 동안 알림 {len(times)}개가 아무 때나 도착 (seed 7)")
    print("2) 짧은 폴링")
    for every in (5, 30):
        r, e, d = short_poll(times, every, hour)
        print(f"   {every:>2}초마다 묻기      요청 {r:4}번 · 빈 응답 {e:4}번 · 평균 지연 {d:4.1f}초")
    r, e, d = long_poll(times, 30, hour)
    print("3) 롱 폴링")
    print(f"   최대 30초 붙잡기   요청 {r:4}번 · 빈 응답 {e:4}번 · 평균 지연 {d:4.1f}초")


if __name__ == "__main__":
    srv = serve()
    try:
        {"1": one, "2": two, "3": three}[sys.argv[1] if len(sys.argv) > 1 else "1"]()
    finally:
        srv.shutdown()
