"""연습 풀이: 제공자는 보냈는데 응답만 끊기면? → 재시도가 두 번 보낸다. 제공자 쪽에서도 id로 걸러야 한 번이 된다."""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from notify import Provider, Service, Transient  # noqa: E402


class LostAck(Provider):
    """보내기는 성공했는데 응답이 사라지는 제공자."""
    def __init__(self, lose, seed, dedup):
        super().__init__(0.0, seed)
        self.lose, self.dedup, self.ids = lose, dedup, set()

    def send(self, msg):
        if not (self.dedup and msg["id"] in self.ids):
            self.got.append(msg["id"]); self.ids.add(msg["id"])
        if self.rnd.random() < self.lose:
            raise Transient("응답 없음")


for dedup in (False, True):
    p = LostAck(0.3, 4, dedup); svc = Service({"push": p})
    for i in range(50):
        svc.submit({"id": f"n{i}", "user": "u", "to": "u", "channel": "push", "kind": "tx", "template": "otp", "data": {"code": i}})
    svc.work("push")
    twice = sum(c > 1 for c in Counter(p.got).values())
    print(f"제공자 id 거르기 {'켬' if dedup else '끔'}: 사용자가 두 번 이상 받은 알림 {twice}개")
