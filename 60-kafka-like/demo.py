"""장난감 Kafka 실행: 1 = 주문 이벤트 12건과 컨슈머 둘, 2 = 셋째 컨슈머가 들어옴(재조정), 3 = 로그 컴팩션."""
import json
import sys
import tempfile

from klog import Group, Topic

STATUS = ["주문됨", "결제됨", "배송됨"]


def produce(topic):
    for st in STATUS:  # 주문 넷이 번갈아 한 단계씩
        for n in range(1, 5):
            topic.append(f"order-{n}", st)


def fresh():
    t = Topic(tempfile.mkdtemp(), "orders", partitions=3, segment_records=4)
    produce(t)
    return t


def show_poll(g, member):
    got = g.poll(member)
    by_key = {}
    for p, r in got:
        by_key.setdefault(r["key"], []).append(r["value"])
    for k, v in sorted(by_key.items()):
        print(f"   {member} ← {k}  {' → '.join(v)}")
    return by_key


def basic():
    t = fresh()
    print("1) 주문 이벤트 12건 → 토픽 orders (파티션 3개)")
    for n in range(1, 5):
        print(f"   키 order-{n} → p{t.partition_of(f'order-{n}')}")
    print("2) 파티션 = 덧붙이기만 하는 파일")
    for p in range(3):
        files = ", ".join(s.name for s in t.segments(p))
        print(f"   p{p}: 오프셋 0~{t.end_offset(p) - 1}  세그먼트 {files}")
    g = Group(t, "shipping")
    g.join("c1"); g.join("c2")
    print("3) 컨슈머 그룹 shipping: " + " / ".join(f"{m} ← " + ",".join(f"p{p}" for p in ps) for m, ps in g.assignment.items()))
    print("4) 각자 읽기")
    seen = {**show_poll(g, "c1"), **show_poll(g, "c2")}
    ok = all(v == STATUS for v in seen.values())
    print(f"5) 키마다 순서: {'모두 주문됨→결제됨→배송됨' if ok else '뒤섞임'}")
    print("   커밋한 오프셋: " + ", ".join(f"p{p}={o}" for p, o in g.committed.items()))


def rebalance():
    t = fresh()
    g = Group(t, "shipping")
    g.join("c1"); g.join("c2"); g.poll("c1"); g.poll("c2")
    print("1) 앞 단계: c1·c2가 12건을 다 읽음, 커밋 " + ", ".join(f"p{p}={o}" for p, o in g.committed.items()))
    for n in (5, 6, 7):
        t.append(f"order-{n}", "주문됨")
    print("2) 새 주문 3건: order-5 → p1, order-6 → p0, order-7 → p2")
    g.join("c3")
    print("3) c3 합류 → 재조정: " + " / ".join(f"{m} ← " + ",".join(f"p{p}" for p in ps) for m, ps in g.assignment.items()))
    print("4) 커밋한 오프셋부터 이어 읽기")
    for m in ("c1", "c2", "c3"):
        show_poll(g, m)
    g.join("c4")
    print(f"5) c4 합류 → c4 몫: {g.assignment['c4'] or '없음'} (파티션 3개, 컨슈머 4명)")


def seg_line(seg):
    recs = [json.loads(l) for l in seg.read_text().splitlines()]
    return " · ".join(f"{r['offset']}:{r['key'][-1]} {r['value']}" for r in recs)


def compaction():
    t = fresh()
    for key, st in (("order-7", "주문됨"), ("order-7", "결제됨"), ("order-3", "반품됨")):
        t.append(key, st)
    print("1) 컴팩션 전 p2: 12건 뒤에 order-7 두 건, order-3 반품 한 건")
    for s in t.segments(2):
        print(f"   {s.name}  " + seg_line(s))
    print("   (칸마다 오프셋:주문 번호 상태)")
    t.compact(2)
    print("2) 키마다 마지막 값만 남기기 (지금 쓰는 마지막 세그먼트는 그대로)")
    for s in t.segments(2):
        print(f"   → {s.name}  " + seg_line(s))
    print("   00000000.log는 남길 게 없어서 통째로 지움")
    print("3) 새 컨슈머가 오프셋 0부터 읽으면")
    print("   " + " / ".join(f"{r['key']} {r['value']}" for r in t.read(2, 0)))
    print("   주문마다 최신 상태만 · 오프셋 번호는 그대로")


if __name__ == "__main__":
    {"1": basic, "2": rebalance, "3": compaction}[(sys.argv[1:] or ["1"])[0]]()
