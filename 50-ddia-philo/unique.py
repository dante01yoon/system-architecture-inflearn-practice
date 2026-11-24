"""유일성 제약을 로그로: 같은 아이디 요청은 같은 파티션으로 → 그 파티션은 한 번에 하나씩 처리 → 먼저 온 쪽이 이긴다."""
import zlib

N = 3


def partition(username):
    return zlib.crc32(username.encode()) % N   # 같은 아이디 → 언제나 같은 파티션


def route(requests):
    parts = [[] for _ in range(N)]
    for r in requests:
        parts[partition(r["username"])].append(r)
    return parts


def process(part):
    """파티션 하나를 맡은 소비자: 차례대로, 한 번에 하나씩."""
    taken, seen, out = set(), set(), []
    for r in part:
        if r["request_id"] in seen:            # 손님이 다시 보낸 같은 요청
            out.append((r, "이미 처리됨"))
            continue
        seen.add(r["request_id"])
        if r["username"] in taken:
            out.append((r, "거절"))
        else:
            taken.add(r["username"])
            out.append((r, "수락"))
    return out
