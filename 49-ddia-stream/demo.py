"""스트림 처리 실행: 1 = 이중 쓰기 경쟁 대 CDC, 2 = 이벤트 시각 기준 1분 창과 늦은 이벤트."""
import sys

from stream import SALES, Consumer, by_arrival, clock, dual_write, open_db, set_status, tumbling


def sync():
    db = open_db()
    with db:
        db.execute("INSERT INTO orders VALUES (1, 'Clean Architecture', '주문됨')")
    index = {1: "주문됨"}
    print("1) 주문 1번: DB와 검색 인덱스 모두 '주문됨'")
    print("2) 이중 쓰기: 요청 A(결제 완료)와 B(취소)가 동시에, 각자 DB → 인덱스 순서로")
    steps = [("A", "db", "결제 완료"), ("B", "db", "취소"), ("B", "index", "취소"), ("A", "index", "결제 완료")]
    for who, target, status in dual_write(db, index, steps):
        print(f"   {who}: {'DB' if target == 'db' else '인덱스'} ← {status}")
    row = db.execute("SELECT status FROM orders WHERE id = 1").fetchone()[0]
    print(f"   결과  DB: {row} / 인덱스: {index[1]} → {'같음' if row == index[1] else '어긋남'}")

    db = open_db()
    with db:
        db.execute("INSERT INTO orders VALUES (1, 'Clean Architecture', '주문됨')")
    set_status(db, 1, "결제 완료"); set_status(db, 1, "취소")
    print("3) CDC: 앱은 DB에만 쓴다. 소비자가 변경 로그를 순서대로 적용")
    search = Consumer(db)
    print("   변경 로그: " + " · ".join(f"#{seq} {st}" for seq, _, st in search.poll()))
    row = db.execute("SELECT status FROM orders WHERE id = 1").fetchone()[0]
    print(f"   결과  DB: {row} / 인덱스: {search.view[1]} → {'같음' if row == search.view[1] else '어긋남'}")
    cache = Consumer(db)
    cache.poll()
    print(f"4) 새 캐시를 오프셋 0부터 채우기: {cache.view[1]} (오프셋 {cache.offset})")
    search.offset = 1; search.poll()
    print(f"5) 같은 변경을 한 번 더 받아도: {search.view[1]} (덮어쓰기라 멱등)")


def windows():
    print("1) 판매 이벤트 12건 — 일어난 시각과 도착한 시각이 다르다")
    for t, arrived, won in SALES:
        if arrived - t > 10:
            print(f"   늦게 옴: {clock(t)}에 판매 → {clock(arrived)}에 도착")
    print("2) 도착 시각으로 1분씩 (처리 시각 기준)")
    for start, wons in by_arrival(SALES):
        print(f"   {clock(start)[:5]} 창  {len(wons)}건  {sum(wons):7,}원")
    print("3) 일어난 시각으로 1분씩 (이벤트 시각 기준, 30초 더 기다림)")
    closed, late = tumbling(SALES)
    for start, wons, at in closed:
        when = f"{clock(at)} 도착 때 닫힘" if at else "끝에서 닫힘"
        print(f"   {clock(start)[:5]} 창  {len(wons)}건  {sum(wons):7,}원  ({when})")
    for t, arrived, won in late:
        print(f"4) 창이 닫힌 뒤 도착: {clock(t)} 판매 {won:,}원 → 따로 보관")


if __name__ == "__main__":
    {"1": sync, "2": windows}[(sys.argv[1:] or ["1"])[0]]()
