"""안정 해시(consistent hashing) — 고리, 가상 노드, 복제 자리. 표준 라이브러리만."""
import bisect
import hashlib


def h(s):
    """md5 앞 16자리 → 64비트 정수(파이썬 hash()는 실행마다 바뀐다)."""
    return int(hashlib.md5(s.encode()).hexdigest()[:16], 16)


def mod_n(key, nodes):
    return nodes[h(key) % len(nodes)]


class Ring:
    def __init__(self, nodes, vnodes=1):
        self.vnodes = vnodes
        self.points = []                 # (위치, 노드) — 위치 순으로 정렬
        for n in nodes:
            self.add(n)

    def add(self, node):
        for i in range(self.vnodes):
            bisect.insort(self.points, (h(f"{node}#{i}"), node))

    def remove(self, node):
        self.points = [p for p in self.points if p[1] != node]

    def node_for(self, key):
        i = bisect.bisect(self.points, (h(key),))     # 키 위치에서 시계 방향 첫 점
        return self.points[i % len(self.points)][1]   # 끝을 넘으면 0으로 돌아온다

    def replicas(self, key, n):
        """시계 방향으로 걸으며 서로 다른 노드 n개(Dynamo의 선호 목록)."""
        i, out = bisect.bisect(self.points, (h(key),)), []
        n = min(n, len({p[1] for p in self.points}))   # 노드가 n대보다 적으면 있는 만큼
        while len(out) < n:
            node = self.points[i % len(self.points)][1]
            if node not in out:
                out.append(node)
            i += 1
        return out


def moved(keys, before, after):
    """keys 중 주인이 바뀐 비율. before·after는 키 → 노드 함수."""
    return sum(before(k) != after(k) for k in keys) / len(keys)


def load(keys, owner):
    c = {}
    for k in keys:
        c[owner(k)] = c.get(owner(k), 0) + 1
    return c
