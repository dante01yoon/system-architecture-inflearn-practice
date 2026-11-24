"""리더 없는 복제: 복제본 n개에 쓰기는 w개, 읽기는 r개가 답하면 성공. 읽을 땐 버전이 가장 큰 값을 고른다."""
from itertools import combinations


def write(replicas, value, version, to):
    for name in to:
        replicas[name] = (version, value)


def read(replicas, frm):
    return max(replicas[name] for name in frm)       # (버전, 값) 중 버전이 가장 큰 것


def all_reads(replicas, r):
    """r개를 고르는 모든 경우에 무엇을 읽는지."""
    return {frm: read(replicas, frm) for frm in combinations(sorted(replicas), r)}
