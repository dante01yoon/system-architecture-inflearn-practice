"""2단계 커밋(2PC): 코디네이터가 모두에게 준비를 묻고, 모두 예라면 커밋을 알린다."""


class Participant:
    def __init__(self, name):
        self.name, self.state, self.locked = name, "시작", False

    def prepare(self):
        self.state, self.locked = "준비됨", True  # 예라고 답하면, 이제 혼자서는 취소도 커밋도 못 한다
        return True

    def finish(self, decision):
        self.state, self.locked = decision, False


class Coordinator:
    def __init__(self, participants):
        self.parts, self.log = participants, []

    def run(self, crash_after_decision=False):
        votes = [p.prepare() for p in self.parts]                # 1단계: 준비
        self.log.append("커밋" if all(votes) else "취소")         # 결정을 먼저 자기 로그에 적는다
        if crash_after_decision:
            return False                                          # 알리기 전에 멈춤
        self.recover()
        return True

    def recover(self):
        for p in self.parts:                                      # 2단계: 로그의 결정을 알린다
            p.finish(self.log[-1])


def try_update(participant):
    """다른 주문이 같은 행을 바꾸려 할 때: 잠금이 걸려 있으면 기다려야 한다."""
    return "막힘 (잠금)" if participant.locked else "바꿈"
