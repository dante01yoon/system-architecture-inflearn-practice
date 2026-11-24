"""Transactional Outbox 실행: 1 = 그냥 발행 대 아웃박스(죽는 자리 셋), 2 = 폴링 전달자 대 로그 테일링."""
import sys

from outbox import (Consumer, Crash, PollingRelay, TailingRelay, cancel,
                    cleanup, count, open_db, place, place_naive)


def crashes():
    db, broker = open_db(), []
    print("1) 그냥 저장 후 발행: 주문 1번 저장 → 발행 직전에 서버가 죽음")
    try:
        place_naive(db, broker, 1, "Clean Architecture", crash=True)
    except Crash:
        pass
    print(f"   주문 표 {count(db, 'SELECT COUNT(*) FROM orders')}건"
          f" / 브로커 {len(broker)}건 → 이벤트를 잃어버림")

    db, broker = open_db(), []
    print("2) 아웃박스: 주문 2번과 이벤트를 한 트랜잭션에 → 커밋 직후 죽음")
    try:
        place(db, 2, "DDIA", crash="after")
    except Crash:
        pass
    left = count(db, "SELECT COUNT(*) FROM outbox WHERE published = 0")
    print(f"   주문 표 {count(db, 'SELECT COUNT(*) FROM orders')}건 / 아웃박스 미발행 {left}건 / 브로커 {len(broker)}건")
    relay = PollingRelay(db, broker)
    relay.run()
    print(f"3) 전달자가 나중에 돎 → 브로커: {broker[-1]['id']}")

    print("4) 주문 3번: 전달자가 보낸 직후, 표시하기 전에 죽음")
    place(db, 3, "DDIA")
    try:
        relay.run(crash_after_send=True)
    except Crash:
        pass
    relay.run()
    print("   다시 돌면 같은 이벤트를 또 보냄 → "
          + " · ".join(e["id"] for e in broker))
    print("5) 재고 서비스는 이벤트 id로 중복을 확인")
    stock = Consumer()
    for e in broker:
        print(f"   {e['id']} → {stock.handle(e)}")
    print(f"   예약 권수: DDIA {stock.reserved['DDIA']}권 (중복 반영 없음)")
    print(f"6) 정리: 보낸 아웃박스 행 {cleanup(db)}개 삭제")


def relays():
    db = open_db()
    place(db, 1, "Clean Architecture"); place(db, 2, "DDIA"); cancel(db, 1)
    print("1) 아웃박스에 이벤트 3건 (주문 1 생성 · 주문 2 생성 · 주문 1 취소)")
    for seq, eid in db.execute("SELECT seq, event_id FROM outbox"):
        print(f"   seq {seq}  {eid}")
    a, b = [], []
    poll = PollingRelay(db, a)
    print(f"2) 폴링 전달자: 미발행 {poll.run()}건을 seq 순서로 → published = 1")
    print("   보낸 순서: " + " → ".join(e["id"] for e in a))
    print(f"   한 번 더 폴링: {poll.run()}건 (할 일 없어도 표를 계속 조회)")
    tail = TailingRelay(db, b)
    print(f"3) 로그 테일링 흉내(트리거가 채운 txlog): {tail.run()}건, 오프셋 {tail.offset}")
    print("   보낸 순서: " + " → ".join(e["id"] for e in b))
    one = [e["type"] for e in a if e["key"] == 1]
    print(f"4) 주문 1번만 보면: {' → '.join(one)}"
          f" ({'두 방식 같음' if a == b else '다름'})")


if __name__ == "__main__":
    {"1": crashes, "2": relays}[(sys.argv[1:] or ["1"])[0]]()
