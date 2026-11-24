"""연습 풀이: 「day = ?」만 묻는 질의가 인덱스를 타게 하기. 실행: python3 solutions/day_index.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from db import build, plan, work

Q = "SELECT * FROM orders WHERE day = ?"
db = build()
db.execute("CREATE INDEX by_user_day ON orders(user_id, day)")
print("(user_id, day)만 있을 때:", plan(db, Q, (300,)), "· 명령", f"{work(db, Q, (300,))[1]:,}개")
db.execute("CREATE INDEX by_day ON orders(day)")   # 질의가 맨 앞 칸으로 쓰는 열에 인덱스를 하나 더
print("(day) 인덱스를 더하면:", plan(db, Q, (300,)), "· 명령", f"{work(db, Q, (300,))[1]:,}개")
print("대가: 인덱스가 하나 늘면 쓸 때마다 고칠 곳도 하나 늘어난다")
