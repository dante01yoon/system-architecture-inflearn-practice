"""연습 문제 풀이: 친구와 나란히 두 자리 — 전부 잡거나 하나도 안 잡기(한 트랜잭션)."""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from seat import hold, open_event, view  # noqa: E402


def hold_many(db, who, seats, now, ttl=300):
    db.execute("BEGIN IMMEDIATE")
    vers = [hold(db, who, s, now, ttl) for s in seats]
    if None in vers:
        db.execute("ROLLBACK")                   # 하나라도 못 잡으면 잡은 것까지 되돌린다
        return None
    db.execute("COMMIT")
    return vers


if __name__ == "__main__":
    db = open_event(os.path.join(tempfile.mkdtemp(), "s.db"), ["B-7", "B-8"], unique=True)
    hold(db, "준호", "B-8", 0)
    print("민지 B-7 + B-8 →", hold_many(db, "민지", ["B-7", "B-8"], 10), "/ B-7:", view(db, "B-7", 10))
    print("민지 B-7 + B-8 (준호 만료 뒤) →", hold_many(db, "민지", ["B-7", "B-8"], 400))
