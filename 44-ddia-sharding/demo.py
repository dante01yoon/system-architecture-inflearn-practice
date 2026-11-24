"""python3 demo.py 1 → 키 범위 대 해시,  2 → 샤드를 4개에서 5개로,  3 → 인기 작가 키와 salting"""
import random
import sys

from shard import by_hash, by_range, count, moved_fixed, moved_mod_n, orders, range_bounds, salted, today_orders

SHARDS = 4


def bar(n, full):
    return "#" * round(20 * n / full)


def one():
    old = orders()
    date_key = lambda o: f"{o[1]}/{o[0]}"   # 키 범위: 주문 날짜(+번호)
    bounds = range_bounds([date_key(o) for o in old], SHARDS)
    rng = count([by_range(date_key(o), bounds) for o in old], SHARDS)
    hsh = count([by_hash(o[0], SHARDS) for o in old], SHARDS)
    print(f"1) 지난 30일 주문 {len(old):,}건 · 샤드 {SHARDS}개")
    print("        키 범위(주문 날짜)        해시(주문 번호)")
    for s in range(SHARDS):
        print(f"   s{s}   {bar(rng[s], 6000):<20} {rng[s]:5,}   {bar(hsh[s], 6000):<20} {hsh[s]:5,}")
    new = today_orders()
    rng = count([by_range(date_key(o), bounds) for o in new], SHARDS)
    hsh = count([by_hash(o[0], SHARDS) for o in new], SHARDS)
    print(f"2) 오늘(11/14) 새 주문 {len(new):,}건이 가는 곳")
    for s in range(SHARDS):
        print(f"   s{s}   {bar(rng[s], 1000):<20} {rng[s]:5,}   {bar(hsh[s], 1000):<20} {hsh[s]:5,}")
    week = [o for o in old if "2026-11-01" <= str(o[1]) <= "2026-11-03"]
    r = {by_range(date_key(o), bounds) for o in week}
    hs = {by_hash(o[0], SHARDS) for o in week}
    print(f"3) 날짜 범위 조회 11/01~11/03 ({len(week):,}건)이 들르는 샤드")
    print(f"   키 범위 {len(r)}개 · 해시 {len(hs)}개(전부)")


def two():
    keys = [o[0] for o in orders()]
    print(f"1) 주문 {len(keys):,}건, 샤드를 4개에서 5개로 늘리면")
    print(f"   해시 mod N    옮길 주문 {moved_mod_n(keys, 4, 5):6.1%}")
    frac, parts = moved_fixed(keys, 64, 4, 5)
    print(f"   파티션 64개   옮길 주문 {frac:6.1%}  (파티션 {parts}개만 새 노드로)")
    print("2) 이상적인 값 = 새 노드 몫 1/5 = 20.0%")


def three():
    rnd = random.Random(3)
    hot = ["작가007"] * 10_000
    print("1) 인기 작가 신간 발매 · 1분 주문 10,000건 (키 = 작가)")
    c = count([by_hash(k, SHARDS) for k in hot], SHARDS)
    for s in range(SHARDS):
        print(f"   s{s}   {bar(c[s], 10000):<20} {c[s]:6,}")
    print("2) 키 뒤에 #0~#15를 붙이면 (salting)")
    c = count([by_hash(salted(k, rnd), SHARDS) for k in hot], SHARDS)
    for s in range(SHARDS):
        print(f"   s{s}   {bar(c[s], 10000):<20} {c[s]:6,}")
    print("3) 대가: 이 작가 주문을 읽으려면 키 16개를 모두 읽어 합친다")


if __name__ == "__main__":
    {"1": one, "2": two, "3": three}[sys.argv[1] if len(sys.argv) > 1 else "1"]()
