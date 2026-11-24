"""연습 풀이: 읽을 때 옛 버전을 들고 있던 복제본을 고쳐 둔다(읽기 복구). python3 solutions/read_repair.py (sdi-kv 폴더에서)"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kv import Cluster  # noqa: E402


def get_and_repair(c, key):
    ok, vs, ctx = c.get(key)
    fixed = 0
    for x in [x for x in c.walk(key) if c.nodes[x].up][:c.N]:
        if c.nodes[x].data.get(key, []) != vs:
            for v, cl in vs:
                c.nodes[x].store(key, v, cl)
            fixed += 1
    return vs, fixed


c = Cluster(["n0", "n1", "n2", "n3", "n4"])
o = c.walk("k")
c.put("k", "v1")
ctx = c.get("k")[2]
c.nodes[o[2]].up = False; c.put("k", "v2", ctx); c.nodes[o[2]].up = True
c.nodes[o[3]].hints.clear()                       # 힌트를 잃었다고 치자
print("고치기 전:", [c.nodes[x].data["k"][0][0] for x in o[:3]])
vs, fixed = get_and_repair(c, "k")
print("읽은 값:", [v for v, _ in vs], "· 고친 복제본", fixed, "개")
print("고친 뒤:", [c.nodes[x].data["k"][0][0] for x in o[:3]])
