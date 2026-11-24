"""연습 풀이: 손님 한 명당 쿠폰 하나. 키 = 손님 아이디 → 같은 손님 요청은 같은 파티션에서 차례대로."""
import zlib

N = 3
CLAIMS = [("c1", "minji", "WELCOME"), ("c2", "junho", "WELCOME"), ("c3", "minji", "WELCOME"), ("c1", "minji", "WELCOME")]


def run(claims):
    parts = [[] for _ in range(N)]
    for c in claims:
        parts[zlib.crc32(c[1].encode()) % N].append(c)
    out = []
    for part in parts:
        used, seen = set(), set()
        for rid, user, coupon in part:
            if rid in seen:
                out.append((rid, user, "이미 처리됨")); continue
            seen.add(rid)
            ok = (user, coupon) not in used
            used.add((user, coupon))
            out.append((rid, user, "발급" if ok else "거절"))
    return out


if __name__ == "__main__":
    res = run(CLAIMS)
    for r in res:
        print(*r)
    assert res == run(CLAIMS) and sorted(r[:2] for r in res if r[2] == "발급") == [("c1", "minji"), ("c2", "junho")]
