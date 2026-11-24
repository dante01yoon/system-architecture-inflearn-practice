"""python3 demo.py 1 → 노드를 4대에서 5대로,  2 → 가상 노드와 고른 정도"""
import sys

from chash import Ring, load, mod_n, moved

KEYS = [f"order:{i}" for i in range(100_000)]
N4 = ["n0", "n1", "n2", "n3"]
N5 = N4 + ["n4"]


def bar(n, full):
    return "#" * round(30 * n / full)


def one():
    print(f"1) 키 {len(KEYS):,}개, 노드를 4대에서 5대로 늘리면 옮길 키")
    print(f"   해시 mod N          {moved(KEYS, lambda k: mod_n(k, N4), lambda k: mod_n(k, N5)):6.1%}")
    for v in (1, 100):
        a, b = Ring(N4, v), Ring(N5, v)
        print(f"   고리 · 가상 노드 {v:<3} {moved(KEYS, a.node_for, b.node_for):6.1%}")
    print("2) 이상적인 값 = 새 노드 몫 1/5 = 20.0%")
    a, b = Ring(N5, 100), Ring(N4, 100)
    print(f"3) 고리에서 n4를 빼면 옮길 키 {moved(KEYS, a.node_for, b.node_for):6.1%} (n4가 맡던 키만)")


def two():
    for i, v in enumerate((1, 100), 1):
        c = load(KEYS, Ring(N4, v).node_for)
        print(f"{i}) 노드 4대 · 가상 노드 {v}개씩")
        for n in N4:
            print(f"   {n}  {bar(c[n], 60_000):<30} {c[n]:6,}")
        print(f"   가장 많음 / 가장 적음 = {max(c.values()) / min(c.values()):.1f}배")
    print(f"3) order:42를 복제할 세 노드: {', '.join(Ring(N4, 100).replicas('order:42', 3))}")


if __name__ == "__main__":
    {"1": one, "2": two}[sys.argv[1] if len(sys.argv) > 1 else "1"]()
