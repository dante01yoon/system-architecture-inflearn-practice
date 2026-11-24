"""연습 문제 풀이: 작가 사인회 마지막 한 자리 — 팬텀으로 생기는 write skew와, 좌석을 줄로 만들어 막기(장난감 모델)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from txn import Conflict, Store  # noqa: E402

CAP = 30


def book(tx, who, seat_rows):
    """정원보다 적게 예약됐으면 내 예약을 추가한다."""
    taken = [k for k in tx.store.versions if k.startswith("예약:") and tx.read(k)]
    if len(taken) >= CAP:
        return False
    if seat_rows:   # 고침: 자리마다 미리 만들어 둔 줄 「자리:30」을 둘 다 고치게 된다
        tx.write(f"자리:{len(taken) + 1}", who)
    tx.write(f"예약:{who}", 1)   # 새 줄 — 상대 스냅샷에는 없던 줄(팬텀)
    return True


for seat_rows in (False, True):
    data = {f"예약:손님{i}": 1 for i in range(CAP - 1)}
    data.update({f"자리:{i + 1}": "" for i in range(CAP)})
    db = Store(data)
    a, b = db.begin(), db.begin()
    book(a, "점원A의 손님", seat_rows); book(b, "점원B의 손님", seat_rows)
    out = []
    for name, tx in (("A", a), ("B", b)):
        try:
            tx.commit(); out.append(f"{name} OK")
        except Conflict:
            out.append(f"{name} 실패")
    final = sum(1 for k in db.versions if k.startswith("예약:") and db.begin().read(k))
    print(f"{'좌석 줄 있음' if seat_rows else '예약 줄만'}: {' · '.join(out)} → 예약 {final}명 (정원 {CAP})")
