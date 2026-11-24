"""연습 풀이: 재시도 예산(토큰 통). 재시도할 때마다 토큰 하나를 쓰고, 성공한 요청 10건마다 하나가 찬다. 통이 비면 재시도하지 않고 바로 실패."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from retry import backoff  # noqa: E402


class RetryBudget:
    def __init__(self, tokens=5, refill_every=10):
        self.tokens, self.refill_every, self.ok = tokens, refill_every, 0

    def call(self, fn, attempts, rng, sleep):
        for attempt in range(attempts):
            try:
                result = fn()
            except ConnectionError:
                if attempt == attempts - 1 or self.tokens < 1:
                    raise
                self.tokens -= 1
                sleep(backoff(attempt, rng=rng))
                continue
            self.ok += 1
            if self.ok % self.refill_every == 0:
                self.tokens += 1
            return result


if __name__ == "__main__":
    sent = []

    def down():
        sent.append(1)
        raise ConnectionError

    budget = RetryBudget(tokens=5)
    for _ in range(20):  # 서버가 멈춘 동안 요청 20건
        try:
            budget.call(down, 3, None, lambda s: None)
        except ConnectionError:
            pass
    assert budget.tokens == 0 and len(sent) == 25
    print("요청 20건, 실제로 보낸 횟수", len(sent), "(예산 없으면 60)")
