"""연습 풀이: 성능이 두 배인 노드에 가상 노드를 두 배로 주면 키도 두 배쯤 받는다."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from chash import Ring, load  # noqa: E402

keys = [f"order:{i}" for i in range(100_000)]
r = Ring([], 100)
for n in ["n0", "n1", "n2"]:
    r.add(n)
r.vnodes = 200   # big은 가상 노드 200개
r.add("big")
c = load(keys, r.node_for)
for n in ["n0", "n1", "n2", "big"]:
    print(f"{n:4} {c[n]:6,}")
