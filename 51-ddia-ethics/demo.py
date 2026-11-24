"""python3 demo.py 1 = 데이터 최소화 + 가명 · python3 demo.py 2 = crypto-shredding으로 손님 한 명 지우기."""
import sys
from collections import Counter

from privacy import SECRET, minimize, pseudonym
from shred import KeyStore, read_personal, write_order

RAW = [{"user_id": "minji", "name": "김민지", "email": "minji@example.com", "phone": "010-0000-0001", "address": "서울 ○○구",
        "birth": "1995-03-02", "ip": "203.0.113.7", "book": "b1", "price": 36000, "day": "11-14"},
       {"user_id": "junho", "name": "이준호", "email": "junho@example.com", "phone": "010-0000-0002", "address": "부산 ○○구",
        "birth": "1990-07-21", "ip": "203.0.113.9", "book": "b2", "price": 35000, "day": "11-14"},
       {"user_id": "minji", "name": "김민지", "email": "minji@example.com", "phone": "010-0000-0001", "address": "서울 ○○구",
        "birth": "1995-03-02", "ip": "203.0.113.7", "book": "b3", "price": 33000, "day": "11-14"}]


def one():
    print(f"1) 주문 화면이 보낸 이벤트: 칸 {len(RAW[0])}개")
    print("   " + " ".join(RAW[0]))
    events = [minimize(r, "판매 통계") for r in RAW]
    print(f"2) 판매 통계에 필요한 칸만: {' · '.join(events[0])}")
    print(f"3) 아이디 대신 가명: minji → {events[0]['user']} · junho → {events[1]['user']}")
    print(f"   손님별 구매 수는 그대로 셀 수 있음: {dict(Counter(e['user'] for e in events))}")
    print(f"4) 키가 다르면 가명도 다름: minji → {pseudonym('minji', b'other-key')}")
    print(f"   이름 · 전화 · 주소가 남았나: {any(k in e for e in events for k in ('name', 'phone', 'address'))}")


def two():
    log, keys = [], KeyStore()
    for r in RAW:
        write_order(log, keys, pseudonym(r["user_id"], SECRET), r["book"], r["price"], r["day"], r["name"], r["address"])
    print(f"1) 주문 로그 {len(log)}줄 · 손님 키 {len(keys.keys)}개 (이름·주소는 그 손님 키로 암호화)")
    print(f"   로그에 적힌 이름 칸: {log[0]['name'].hex()[:24]}…")
    print("2) 배송 담당이 키로 읽기")
    for i, e in enumerate(log):
        print(f"   #{i} {e['book']}  {read_personal(keys, e, 'name')} · {read_personal(keys, e, 'address')}")
    total = sum(e["price"] for e in log)
    keys.forget(pseudonym("minji", SECRET))
    print("3) minji 탈퇴 → 그 손님 키만 지움 (로그는 한 줄도 안 고침)")
    for i, e in enumerate(log):
        print(f"   #{i} {e['book']}  {read_personal(keys, e, 'name') or '읽을 수 없음'}")
    print(f"4) 매출 합계는 그대로: {total:,}원 → {sum(e['price'] for e in log):,}원")


if __name__ == "__main__":
    {"1": one, "2": two}[sys.argv[1] if len(sys.argv) > 1 else "1"]()
