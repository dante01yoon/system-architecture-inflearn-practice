"""python3 demo.py 1 → 노드 하나가 꺼졌을 때(힌트 · 복구 · Merkle),  2 → 두 손님이 동시에 쓰면(벡터 시계 대 LWW)"""
import sys

from kv import Cluster, diff, tree

NAMES = ["n0", "n1", "n2", "n3", "n4"]
KEY = "cart:dante"


def clk(c):
    return "{" + ", ".join(f"{n}:{v}" for n, v in sorted(c.items())) + "}"


def failure():
    c = Cluster(NAMES)
    order = c.walk(KEY)
    print(f"1) 노드 5대 · N={c.N} W={c.W} R={c.R}")
    print(f"   {KEY} 선호 목록 {' → '.join(order[:3])} · 다음 {order[3]}")
    down = order[1]
    c.nodes[down].up = False
    ok, log, _ = c.put(KEY, ["DDIA"])
    print(f"2) {down} 꺼짐 · put {KEY} = ['DDIA']")
    print("   " + " · ".join(f"{x} 저장" + (f"(힌트 → {to})" if to else "") for x, to in log) + f" · 응답 {len(log)} ≥ W={c.W} → {'성공' if ok else '실패'}")
    ok, vs, _ = c.get(KEY)
    asked = sum(c.nodes[x].up for x in c.walk(KEY)[:4])
    print(f"3) get → {vs[0][0]} · 응답 {min(asked, c.N)} ≥ R={c.R} → {'성공' if ok else '실패'}")
    holder = next(x for x, to in log if to)
    print(f"4) {down} 복구 → {holder}가 힌트 {c.recover(down)}개를 넘김 · {down}: {c.nodes[down].data[KEY][0][0]}")
    # 힌트를 맡은 노드도 함께 죽어 힌트가 사라진 경우: 두 복제본이 조용히 어긋난다
    keys = [f"book:{i:03d}" for i in range(256)]
    a, b = c.nodes[order[0]], c.nodes[order[2]]
    for k in keys:
        a.store(k, 1, {"n0": 1}); b.store(k, 1, {"n0": 1})
    for k in ("book:041", "book:042", "book:200"):
        a.store(k, 2, {"n0": 2})
    leaves, cmp = diff(tree(a, keys), tree(b, keys))
    print(f"5) 힌트를 잃었다면: {a.name}와 {b.name} 키 256개 중 몇 개가 다름")
    print(f"   Merkle 비교: 해시 {cmp}개 비교 → 다른 구간 {len(leaves)}개 " + " ".join(f"[{keys[i * 16]}~{keys[i * 16 + 15][-3:]}]" for i in leaves))
    bad = [k for i in leaves for k in keys[i * 16:i * 16 + 16] if a.data[k] != b.data[k]]
    print(f"   그 구간 키 {len(leaves) * 16}개만 보고 {len(bad)}개 다시 보냄: {' '.join(bad)}")


def conflict():
    c = Cluster(NAMES)
    order = c.walk(KEY)
    _, _, base = c.put(KEY, [])
    print(f"1) 빈 장바구니 · 시계 {clk(base)}")
    _, _, ca = c.put(KEY, ["DDIA"], base, coord=order[0])
    _, _, cb = c.put(KEY, ["클린 코드"], base, coord=order[1])
    print(f"2) 손님 A → {order[0]}: ['DDIA']      시계 {clk(ca)}")
    print(f"   손님 B → {order[1]}: ['클린 코드'] 시계 {clk(cb)}")
    ok, vs, ctx = c.get(KEY)
    print(f"3) get → 버전 {len(vs)}개 · 서로 모름 = 충돌")
    for v, cc in vs:
        print(f"   {v} {clk(cc)}")
    merged = sorted({b for v, _ in vs for b in v})
    _, _, cm = c.put(KEY, merged, ctx)
    print(f"4) 앱이 합쳐 다시 put → {merged} 시계 {clk(cm)}")
    print(f"   get → 버전 {len(c.get(KEY)[1])}개")
    stamps = {"DDIA": 1000.020, "클린 코드": 1000.015}    # 두 서버 시계(가정): A 쪽이 5ms 앞서 있음
    lww = max(stamps, key=stamps.get)
    print(f"5) LWW였다면: 시각이 큰 하나만 남김 → ['{lww}'] · '{min(stamps, key=stamps.get)}' 사라짐")


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "1"
    {"1": failure, "2": conflict}[arg]()
