"""설정 파일에서 분산 모놀리스 신호 세 가지를 찾는다: 같이 배포, 깊은 동기 호출, 공유 DB."""
import json
from itertools import combinations


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def lockstep(deploys, at_least=3):
    """늘 같이 배포된 서비스 쌍: 한쪽이 나갈 때마다 다른 쪽도 나갔다."""
    names = sorted({s for d in deploys for s in d})
    pairs = []
    for a, b in combinations(names, 2):
        n_a = sum(a in d for d in deploys)
        n_b = sum(b in d for d in deploys)
        both = sum(a in d and b in d for d in deploys)
        if both >= at_least and both == n_a == n_b:
            pairs.append((a, b, both))
    return pairs


def deepest(calls, start, seen=()):
    """start에서 동기 호출을 따라간 가장 긴 사슬(서비스 이름 목록)."""
    best = [start]
    for nxt in calls.get(start, []):
        if nxt in seen:
            continue  # 순환 호출은 한 번만 따라간다
        path = [start] + deepest(calls, nxt, seen + (start,))
        if len(path) > len(best):
            best = path
    return best


def long_chains(calls, entries, limit=2):
    """입구 서비스에서 시작해 limit 홉보다 깊은 사슬들."""
    return [c for c in (deepest(calls, e) for e in entries) if len(c) - 1 > limit]


def shared_dbs(dbs):
    """DB 하나를 서비스 둘 이상이 같이 쓰는 경우."""
    owners = {}
    for svc, db in dbs.items():
        owners.setdefault(db, []).append(svc)
    return {db: s for db, s in owners.items() if len(s) > 1}


def diagnose(cfg, limit=2):
    return {
        "lockstep": lockstep(cfg["deploys"]),
        "chains": long_chains(cfg["calls"], cfg["entries"], limit),
        "shared": shared_dbs(cfg["dbs"]),
    }
