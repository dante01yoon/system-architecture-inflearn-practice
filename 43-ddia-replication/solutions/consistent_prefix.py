"""연습 문제 풀이: 질문과 답이 서로 다른 팔로워를 거치면 답이 질문보다 먼저 보인다(consistent prefix 깨짐).
고침: 서로 이어진 글(같은 질문의 글타래)은 같은 팔로워 하나로 읽는다."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from replica import Follower, Leader  # noqa: E402

q_leader, a_leader = Leader(), Leader()      # 질문과 답이 서로 다른 샤드(리더)에 저장됨
q_f = Follower("fq", q_leader, lag=800)
a_f = Follower("fa", a_leader, lag=100)
q_leader.write("q", "배송 언제 와요?", now=0)
a_leader.write("a", "내일 도착해요", now=200)
t = 400
print(f"1) t={t}ms 따로 읽기: 질문={q_f.read('q', t) or '(없음)'}, 답={a_f.read('a', t) or '(없음)'}  → 답이 먼저 보임")
one = Leader()
f = Follower("f1", one, lag=300)
one.write("q", "배송 언제 와요?", now=0)
one.write("a", "내일 도착해요", now=200)
for k, t in ((2, 400), (3, 600)):
    q, a = f.read("q", t), f.read("a", t)
    print(f"{k}) t={t}ms 같은 로그·같은 팔로워: 질문={q or '(없음)'}, 답={a or '(없음)'}")
