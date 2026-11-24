"""미디에이터 토폴로지: 지휘자 하나가 단계 목록을 순서대로 부르고, 실패하면 되돌린다."""


class Mediator:
    def __init__(self, steps):
        self.steps, self.log = steps, []   # steps = [(이름, 할 일, 되돌릴 일)]

    def run(self, order):
        done = []
        for name, do, undo in self.steps:
            self.log.append(f"#{order['id']} {name}")
            try:
                do(order)
            except Exception as e:
                for back in reversed(done):  # 이미 끝낸 단계를 거꾸로 되돌린다
                    back(order)
                return f"실패: {name} ({e}), 되돌린 단계 {len(done)}개"
            done.append(undo)
        return "완료"
