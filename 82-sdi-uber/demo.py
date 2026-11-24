"""python3 demo.py 1 → 가까운 기사 찾기(geohash 대 전부 확인),  2 → 두 손님이 같은 기사를 동시에 부르면"""
import random
import sys

from geo import Index, box, dist, encode, neighbors
from match import ACCEPT, Store, dispatch, race

GANGNAM = (37.4979, 127.0276)   # 강남역 근처


def seoul(n=10_000, seed=7):
    """서울 안에 기사 n명을 seed로 고정해 흩어 놓는다(위치는 가정)."""
    rnd, idx = random.Random(seed), Index()
    for i in range(n):
        idx.update(f"d{i}", rnd.uniform(37.45, 37.65), rnd.uniform(126.85, 127.15), now=0)
    return idx


def search():
    idx = seoul()
    gh = encode(*GANGNAM)
    s, n, w, e = box(gh)
    print(f"1) 기사 {len(idx.pos):,}명 · 강남역 {GANGNAM[0]}, {GANGNAM[1]}")
    print(f"   geohash {gh} · 칸 {dist((s, w), (s, e)):,.0f}m × {dist((s, w), (n, w)):,.0f}m")
    print(f"   이웃 여덟 칸: {' '.join(neighbors(gh))}")
    print("2) 반경 500m 안의 기사")
    idx.checks = 0; a = idx.brute(GANGNAM, 500, now=5); full = idx.checks
    idx.checks = 0; b = idx.nearby(GANGNAM, 500, now=5); cell = idx.checks
    print(f"   전부 확인    거리 계산 {full:>6,}번 · {len(a)}명")
    print(f"   geohash 9칸  거리 계산 {cell:>6,}번 · {len(b)}명")
    print(f"   같은 결과: {a == b} · 계산 {full / cell:.0f}분의 1")
    print("3) 가까운 순 셋: " + " · ".join(f"{d} {m}m" for m, d in b[:3]))
    m, d = b[0]
    for k in idx.pos:
        if k != d:
            idx.update(k, *idx.pos[k][0], now=35)    # 다른 기사는 계속 위치를 보낸다
    print(f"4) {d}만 30초 넘게 소식 없음 → 다시 찾으면 맨 앞은 {idx.nearby(GANGNAM, 500, now=40)[0][1]}")


def assign():
    idx = seoul()
    cands = idx.nearby(GANGNAM, 500, now=5)[:3]
    print("1) 손님 r1 · r2가 강남역에서 동시에 호출")
    print("   후보(가까운 순): " + " · ".join(f"{d} {m}m" for m, d in cands))
    got = race(Store(), ["r1", "r2"], cands, now=5, naive=True)
    print(f"2) 확인하고 쓰기  r1 → {got['r1']} · r2 → {got['r2']}  (한 기사에 두 손님)")
    st = Store()
    got = race(st, ["r1", "r2"], cands, now=5)
    first, second = sorted(got.values(), key=lambda d: [c[1] for c in cands].index(d))
    print(f"3) 원자적 잡기    먼저 잡은 손님 → {first} · 늦은 손님 → {second}  (다음 가까운 기사)")
    late = dispatch(st, "r3", cands, now=5 + ACCEPT - 1)
    print(f"4) 9초 뒤 r3 → {late}  (앞 두 기사는 아직 수락 대기)")
    again = dispatch(st, "r4", cands, now=5 + ACCEPT + 1)
    print(f"5) {ACCEPT}초 안에 수락 없음 → 리스 끝 · r4 → {again}")


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "1"
    {"1": search, "2": assign}[arg]()
