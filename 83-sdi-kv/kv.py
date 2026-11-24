"""Dynamo 방식 키-값 저장소를 한 프로세스 안에: 고리 · N개 복제 · W/R · sloppy quorum + 힌트 · 벡터 시계 · Merkle 트리"""
import bisect
import hashlib


def h(s):
    return int(hashlib.md5(s.encode()).hexdigest(), 16)


# ── 벡터 시계: {노드: 횟수} ──
def descends(a, b):
    """a가 b를 이미 담고 있나(모든 노드의 횟수가 b 이상)."""
    return all(a.get(n, 0) >= c for n, c in b.items())


def merge(*clocks):
    out = {}
    for c in clocks:
        for n, v in c.items():
            out[n] = max(out.get(n, 0), v)
    return out


class Node:
    def __init__(self, name):
        self.name, self.up, self.data, self.hints = name, True, {}, []

    def store(self, key, value, clock):
        """새 버전이 덮는 옛 버전은 버리고, 서로 모르는 버전은 함께 둔다."""
        old = self.data.get(key, [])
        if any(descends(c, clock) for _, c in old):
            return
        self.data[key] = [(v, c) for v, c in old if not descends(clock, c)] + [(value, clock)]


class Cluster:
    def __init__(self, names, n=3, w=2, r=2, vnodes=8):
        self.nodes = {x: Node(x) for x in names}
        self.N, self.W, self.R = n, w, r
        self.ring = sorted((h(f"{x}#{i}"), x) for x in names for i in range(vnodes))

    def walk(self, key):
        """키 자리에서 시계 방향으로 서로 다른 노드를 차례로(선호 목록 + 그 뒤)."""
        i, seen = bisect.bisect(self.ring, (h(key), "")), []
        for k in range(len(self.ring)):
            x = self.ring[(i + k) % len(self.ring)][1]
            if x not in seen:
                seen.append(x)
        return seen

    def put(self, key, value, ctx=None, coord=None):
        """앞쪽 N개 중 꺼진 노드 몫은 다음 건강한 노드가 힌트와 함께 받는다. 응답 W개면 성공."""
        order = self.walk(key)
        want, spare = order[:self.N], [x for x in order[self.N:] if self.nodes[x].up]
        coord = coord or next(x for x in want if self.nodes[x].up)
        clock = merge(ctx or {}); clock[coord] = clock.get(coord, 0) + 1
        log = []
        for x in want:
            if self.nodes[x].up:
                self.nodes[x].store(key, value, clock); log.append((x, None))
            elif spare:
                y = spare.pop(0)
                self.nodes[y].store(key, value, clock)
                self.nodes[y].hints.append((x, key, value, clock))   # 원래 주인 x
                log.append((y, x))
        return len(log) >= self.W, log, clock

    def get(self, key):
        """건강한 앞쪽 N개에게 묻고 R개 이상이면, 서로 모르는 버전을 모두 돌려준다(앱이 합친다)."""
        ask = [x for x in self.walk(key) if self.nodes[x].up][:self.N]
        vs = [vc for x in ask for vc in self.nodes[x].data.get(key, [])]
        keep = []
        for v, c in vs:
            if not any(descends(c2, c) and c2 != c for _, c2 in vs) and (v, c) not in keep:
                keep.append((v, c))
        return len(ask) >= self.R, keep, merge(*[c for _, c in keep])

    def recover(self, name):
        """돌아온 노드에게 다른 노드들이 맡아 둔 힌트를 넘긴다."""
        self.nodes[name].up, moved = True, 0
        for nd in self.nodes.values():
            for hint in [t for t in nd.hints if t[0] == name]:
                _, key, value, clock = hint
                self.nodes[name].store(key, value, clock)
                nd.hints.remove(hint); moved += 1
        return moved


# ── Merkle 트리: 키 구간마다 잎 해시, 위로 갈수록 두 자식의 해시 ──
def tree(node, keys, leaves=16):
    step = len(keys) // leaves
    level = [h(repr([(k, node.data.get(k)) for k in keys[i * step:(i + 1) * step]]))
             for i in range(leaves)]
    t = [level]
    while len(level) > 1:
        level = [h(f"{level[i]}{level[i + 1]}") for i in range(0, len(level), 2)]
        t.append(level)
    return t[::-1]     # t[0] = 루트


def diff(a, b):
    """루트부터 같은 칸끼리 비교해 내려간다. (다른 잎 번호들, 비교한 해시 수)."""
    todo, cmp = [0], 0
    for d in range(len(a)):
        nxt = []
        for i in todo:
            cmp += 1
            if a[d][i] != b[d][i]:
                nxt += [2 * i, 2 * i + 1] if d + 1 < len(a) else [i]
        todo = nxt
    return todo, cmp
