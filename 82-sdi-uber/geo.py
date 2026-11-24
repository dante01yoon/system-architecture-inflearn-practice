"""geohash 인코딩 · 이웃 칸 · 기사 위치 색인(메모리, TTL)"""
import math

BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"   # a · i · l · o 가 없는 32글자
TTL = 30                                     # 이 초 동안 위치가 안 오면 검색에서 뺀다(가정)


def encode(lat, lon, n=6):
    """경도 · 위도 범위를 번갈아 반으로 접어 비트를 만들고, 5비트마다 한 글자."""
    la, lo, bits, out, even = [-90.0, 90.0], [-180.0, 180.0], [], "", True
    while len(out) < n:
        rng, v = (lo, lon) if even else (la, lat)
        even = not even
        mid = (rng[0] + rng[1]) / 2
        if v >= mid:
            bits.append(1); rng[0] = mid
        else:
            bits.append(0); rng[1] = mid
        if len(bits) == 5:
            out += BASE32[int("".join(map(str, bits)), 2)]; bits = []
    return out


def box(gh):
    """칸의 범위 (위도 최소, 최대, 경도 최소, 최대)."""
    la, lo, even = [-90.0, 90.0], [-180.0, 180.0], True
    for c in gh:
        for b in format(BASE32.index(c), "05b"):
            rng = lo if even else la
            mid = (rng[0] + rng[1]) / 2
            rng[0 if b == "1" else 1] = mid
            even = not even
    return la[0], la[1], lo[0], lo[1]


def neighbors(gh):
    """둘레 여덟 칸: 가운데 칸 크기만큼 위아래 · 옆으로 옮겨 다시 인코딩."""
    # shortcut: 극 · 날짜 변경선 근처는 다루지 않는다, 전 세계용이면 그 경계를 따로 처리
    s, n, w, e = box(gh)
    clat, clon, dlat, dlon = (s + n) / 2, (w + e) / 2, n - s, e - w
    return [encode(clat + i * dlat, clon + j * dlon, len(gh))
            for i in (1, 0, -1) for j in (-1, 0, 1) if i or j]


def dist(a, b):
    """두 점 사이 거리(미터, 하버사인)."""
    la1, lo1, la2, lo2 = map(math.radians, (*a, *b))
    h = (math.sin((la2 - la1) / 2) ** 2
         + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2)
    return 2 * 6_371_000 * math.asin(math.sqrt(h))


class Index:
    """기사 위치를 메모리에: 칸 → 기사들, 기사 → (위치, 마지막 소식 시각)."""

    def __init__(self, n=6):
        self.n, self.cells, self.pos, self.checks = n, {}, {}, 0

    def update(self, d, lat, lon, now):
        old = self.pos.get(d)
        if old:
            self.cells[encode(*old[0], self.n)].discard(d)
        self.pos[d] = ((lat, lon), now)
        self.cells.setdefault(encode(lat, lon, self.n), set()).add(d)

    def nearby(self, p, r, now):
        """가운데 칸 + 이웃 여덟 칸만 보고, 반경 r 안 · TTL 안의 기사를 가까운 순으로."""
        gh = encode(*p, self.n)
        found = []
        for c in [gh] + neighbors(gh):
            for d in self.cells.get(c, ()):
                (q, seen) = self.pos[d]
                if now - seen > TTL:
                    continue
                self.checks += 1
                m = dist(p, q)
                if m <= r:
                    found.append((round(m), d))
        return sorted(found)

    def brute(self, p, r, now):
        """비교용: 모든 기사와 거리를 잰다."""
        found = []
        for d, (q, seen) in self.pos.items():
            if now - seen > TTL:
                continue
            self.checks += 1
            m = dist(p, q)
            if m <= r:
                found.append((round(m), d))
        return sorted(found)
