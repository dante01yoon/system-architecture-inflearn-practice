"""Saga 실행기: 단계 T마다 보상 C를 짝지어 두고, 실패하면 끝낸 단계의 C를 거꾸로 부른다."""


class Saga:
    def __init__(self, steps):
        self.steps = steps    # [(이름, T, C)]
        self.timeline = []    # 일어난 순서대로 남기는 기록

    def run(self, db, order, watch=None):
        done = []
        for i, (name, t, c) in enumerate(self.steps, 1):
            try:
                with db:                      # 단계 하나 = 짧은 트랜잭션 하나
                    t(db, order)
            except Exception as e:
                self.timeline.append(f"T{i} {name} 실패 ({e})")
                for j, back_name, back in reversed(done):  # 끝낸 단계를 거꾸로
                    with db:
                        back(db, order)
                    self.timeline.append(f"C{j} {back_name} 보상")
                return False
            self.timeline.append(f"T{i} {name} 커밋")
            done.append((i, name, c))
            if watch:                         # 커밋 직후, 다른 연결에서 본 모습
                self.timeline.append(f"  · {watch()}")
        return True
