"""python3 demo.py 1 → 인덱스 효과,  2 → 키-값 대 SQL 훑기,  3 → 문제 넷의 DB 고르기"""
import sys
import time
import unicodedata

from db import build, plan, work
from decide import PROBLEMS, suggest

Q_USER = "SELECT * FROM orders WHERE user_id = ?"
Q_BOTH = "SELECT * FROM orders WHERE user_id = ? AND day >= ?"
Q_DAY = "SELECT * FROM orders WHERE day = ?"


def pad(s, w):
    return s + " " * (w - sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s))


def show(db, label, sql, args):
    n, k, ms = work(db, sql, args)
    print(f"   {pad(label, 12)} {plan(db, sql, args)}")
    print(f"   {pad('', 12)} 결과 {n}줄 · 명령 {k:,}개 · {ms:.2f}ms")


def indexes():
    db = build()
    print("1) 주문 200,000줄 · 회원 한 명의 주문 찾기")
    show(db, "인덱스 없음", Q_USER, (42,))
    db.execute("CREATE INDEX by_user ON orders(user_id)")
    show(db, "user_id", Q_USER, (42,))
    db.execute("DROP INDEX by_user")
    db.execute("CREATE INDEX by_user_day ON orders(user_id, day)")
    print("2) 묶음 인덱스 (user_id, day)")
    show(db, "앞 칸부터", Q_BOTH, (42, 200))
    show(db, "뒤 칸만", Q_DAY, (300,))


def keyvalue():
    db = build()
    kv = {row[0]: row for row in db.execute("SELECT * FROM orders")}
    keys = (7, 77_777, 199_999)
    print("1) 같은 주문 3건을 키로 꺼내기")
    t = time.perf_counter()
    found = [kv[k] for k in keys]
    print(f"   {pad('dict', 12)} 키-값 · 해시로 바로 찾기")
    print(f"   {pad('', 12)} 결과 {len(found)}줄 · {(time.perf_counter() - t) * 1000:.4f}ms")
    show(db, "기본 키", "SELECT * FROM orders WHERE id IN (?, ?, ?)", keys)
    show(db, "키를 못 쓰면", "SELECT * FROM orders WHERE id + 0 IN (?, ?, ?)", keys)
    print("2) 키로만 읽는다면 키-값으로 충분하다")


def choose():
    print("1) 면접 문제 넷 · 고른 DB와 이유")
    for name, needs, home in PROBLEMS:
        print(f"   [{name}] 원본 = {home}")
        for kind, why in suggest(needs):
            print(f"      {pad(kind, 12)} ← {why}")
    print("2) 원본 하나 + 필요한 곳에 보조 저장소")


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "1"
    {"1": indexes, "2": keyvalue, "3": choose}[arg]()
