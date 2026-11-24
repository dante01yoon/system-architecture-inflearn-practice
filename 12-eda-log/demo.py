"""큐에서 메시지를 잃고(최대 한 번), 두 번 받고(최소 한 번), 멱등 소비자로 고치고, 로그를 처음부터 다시 읽는다."""
import tempfile
from pathlib import Path

from consumer import left, open_db, take, take_once
from log import Log
from mq import Queue

ORDERS = [{"id": f"m{i}", "book": "DDIA", "qty": 1} for i in (1, 2, 3)]  # 재고 10권에서 1권씩 3번 -> 기대 7권


def at_least_once(handle):
    q, db, got, died = Queue(ORDERS), open_db(), 0, False
    while q.ready:
        msg = q.receive(auto_ack=False)
        got += 1
        handled = handle(db, msg)
        if msg["id"] == "m2" and not died:
            died = True
            q.consumer_died()  # 처리는 했는데 ack를 보내기 전에 죽음
            continue
        q.ack(msg)
        if handled is False:
            print(f"   {msg['id']} 다시 옴 -> 처리한 번호라 건너뜀")
    return got, left(db)


def main():
    print("1) 최대 한 번: 받는 순간 지우는 큐, m2를 처리하기 전에 소비자가 죽음")
    q, db = Queue(ORDERS), open_db()
    while q.ready:
        msg = q.receive(auto_ack=True)
        if msg["id"] == "m2":
            q.consumer_died()
            continue
        take(db, msg)
    print(f"   재고 {left(db)}권 (기대 7권), 큐에 남은 메시지 {len(q.ready)}개 -> m2를 잃어버림")

    print("2) 최소 한 번: 처리한 뒤 ack, m2를 처리하고 ack 전에 소비자가 죽음")
    got, n = at_least_once(take)
    print(f"   받은 메시지 {got}개, 재고 {n}권 (기대 7권) -> m2를 두 번 뺌")

    print("3) 멱등 소비자: 같은 상황, 처리한 번호를 표에 남김")
    got, n = at_least_once(take_once)
    print(f"   받은 메시지 {got}개, 재고 {n}권 (기대 7권)")

    print("4) 로그: 이벤트 3개를 붙이고, 새 소비자가 오프셋 0부터 다시 읽음")
    log = Log(Path(tempfile.mkdtemp()) / "orders.log")
    for e in ORDERS:
        log.append(e)
    for n, e in log.read("stock"):
        log.commit("stock", n)
    print(f"   재고 소비자 오프셋 {log.offsets['stock']}, 파일 줄 수 {len(log.path.read_text().splitlines())} (읽어도 지워지지 않음)")
    sold = 0
    for n, e in log.read("report"):
        sold += e["qty"]
        log.commit("report", n)
    print(f"   새 소비자 매출 집계: 0번부터 {log.offsets['report']}개 다시 읽음, 판매 {sold}권")
    print(f"   오프셋: {log.offsets}")


if __name__ == "__main__":
    main()
