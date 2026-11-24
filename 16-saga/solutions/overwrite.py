"""연습 문제 풀이: 보상을 「그때 값으로 덮어쓰기」로 만들면, 그 사이 다른 손님의 차감이 사라진다.
실행: python3 solutions/overwrite.py (saga 폴더에서)"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import shop  # noqa: E402


def run(release):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE stock(book TEXT PRIMARY KEY, qty INT)")
    db.execute("INSERT INTO stock VALUES ('DDIA', 5)")
    mine = {"book": "DDIA", "qty": 2}
    before = db.execute("SELECT qty FROM stock").fetchone()[0]       # T3가 본 값: 5
    shop.reserve(db, mine)                                            # T3: 5 → 3
    shop.reserve(db, {"book": "DDIA", "qty": 1})                      # 그사이 다른 손님: 3 → 2
    release(db, mine, before)                                         # 내 saga가 실패해 보상
    return db.execute("SELECT qty FROM stock").fetchone()[0]


semantic = run(lambda db, o, before: shop.release(db, o))            # 2 + 2 = 4 (맞음)
overwrite = run(lambda db, o, before: db.execute("UPDATE stock SET qty = ?", (before,)))  # 5 (다른 손님 몫이 사라짐)
print(f"뜻을 되돌리는 보상(+2): 재고 {semantic}권  ← 다른 손님이 가져간 1권이 반영됨")
print(f"그때 값으로 덮어쓰기(=5): 재고 {overwrite}권  ← 다른 손님의 1권이 사라짐")
assert (semantic, overwrite) == (4, 5)
