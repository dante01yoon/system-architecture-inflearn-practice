"""python3 demo.py 1 → Snowflake ID,  2 → base62 길이,  3 → 해시 자르기 겹침,  4 → 짧은 주소 만들고 열기"""
import random
import sys

from idgen import EPOCH_MS, ClockMovedBackwards, Snowflake, encode, parse
from shortener import Shortener, hash_code

NOW_MS = EPOCH_MS + 317 * 86_400_000   # 2026-11-14 00:00 UTC (예제용 고정 시각)


def ticks(offsets):
    it = iter(offsets)
    return lambda: NOW_MS + next(it)


def snowflake():
    print("1) 기계 두 대가 ID를 5개씩 · 같은 1ms 안에서는 순번이 오른다")
    gens = {1: Snowflake(1, ticks([0, 0, 1, 2, 2, 1])), 2: Snowflake(2, ticks([0, 1, 1, 1, 2]))}
    ids = [g.next_id() for g in gens.values() for _ in range(5)]
    print("   ID                    시각    기계  순번  base62")
    for i in sorted(ids):
        ms, m, seq = parse(i)
        print(f"   {i:<20}  +{ms - (NOW_MS - EPOCH_MS)}ms   {m:>3}  {seq:>4}  {encode(i)}")
    by_time = sorted(ids, key=lambda i: (parse(i)[0], parse(i)[1], parse(i)[2]))
    print(f"2) ID 순서 = 시각 순서: {sorted(ids) == by_time} · 서로 다른 ID {len(set(ids))}개 / {len(ids)}개")
    try:
        gens[1].next_id()
    except ClockMovedBackwards as e:
        print(f"3) 기계 1의 시계가 뒤로 → 만들기 거절: {e}")


def lengths():
    print("1) 카운터 값을 base62로 바꾸면")
    for n in (10 ** 6, 10 ** 8, 10 ** 10, 10 ** 12):
        print(f"   {n:>17,}  →  {len(encode(n))}글자  {encode(n)}")
    print(f"2) 7글자에 담기는 수: 62^7 = {62 ** 7:,}")
    sf = Snowflake(1, ticks([0])).next_id()
    print(f"3) Snowflake ID {sf} → base62 {len(encode(sf))}글자")


def collisions(n=1_000_000):
    rnd = random.Random(7)
    urls = {f"https://bookshop.example/b/{rnd.getrandbits(64):x}" for _ in range(n)}
    print(f"1) 서로 다른 URL {len(urls):,}개 · SHA-256 앞부분을 잘라 코드로 (seed 7)")
    for k in (5, 6, 7):
        codes = {hash_code(u, k) for u in urls}
        print(f"   {k}글자 해시   겹친 URL {len(urls) - len(codes):>7,}개")
    counter = {encode(i) for i in range(1, len(urls) + 1)}
    print(f"2) 카운터 + base62  겹친 URL {len(urls) - len(counter)}개")
    m = 10 ** 9
    print(f"3) 7글자 해시 · URL 10억 개라면 예상 겹침 약 {m * m // (2 * 62 ** 7):,}개 (n² ÷ 2N)")


def shortener():
    t = [0]
    s = Shortener(clock=lambda: t[0], start=10 ** 6)
    print("1) POST /urls · 카운터는 1,000,000부터")
    a = s.create("https://bookshop.example/books/ddia-2nd?ref=newsletter")
    b = s.create("https://bookshop.example/books/clean-architecture", alias="clean")
    c = s.create("https://bookshop.example/sale/midnight", ttl=3600)
    print(f"   {a:<6} ← 카운터\n   {b:<6} ← 직접 고른 이름\n   {c:<6} ← 만료 1시간")
    try:
        s.create("https://bookshop.example/other", alias="clean")
    except ValueError as e:
        print(f"2) 같은 이름을 또 달라고 하면 → 거절: {e}")
    print("3) GET /{code}")
    for code in (a, b, c, "zzzz"):
        st, loc = s.redirect(code)
        print(f"   /{code:<6} {st}  {loc or ''}")
    t[0] = 3600
    st, _ = s.redirect(c)
    print(f"4) 1시간 뒤 /{c} → {st} · 만료된 주소")


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "1"
    {"1": snowflake, "2": lengths, "3": collisions, "4": shortener}[arg]()
