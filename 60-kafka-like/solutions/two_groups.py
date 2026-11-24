"""연습 풀이: 같은 토픽을 그룹 둘(shipping, search)이 따로 읽는다 — 오프셋을 그룹마다 따로 기억하니 서로 빼앗지 않는다."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from demo import fresh  # noqa: E402
from klog import Group  # noqa: E402

t = fresh()
ship, search = Group(t, "shipping"), Group(t, "search")
ship.join("c1"); ship.join("c2"); search.join("s1")
n_ship = len(ship.poll("c1")) + len(ship.poll("c2"))
n_search = len(search.poll("s1"))
print(f"shipping 그룹 {n_ship}건, search 그룹 {n_search}건 — 둘 다 12건 전부")
print("shipping 오프셋:", ship.committed, "/ search 오프셋:", search.committed)
assert n_ship == n_search == 12
