"""재시도: 기다리는 시간을 두 배씩 늘리고(지수 백오프), 그 안에서 무작위로 고른다(지터)."""


def backoff(attempt, base=1.0, cap=8.0, rng=None):
    delay = min(cap, base * 2 ** attempt)  # 1 → 2 → 4 → 8초, 더는 늘리지 않는다
    return rng.uniform(0, delay) if rng else delay


def retry(fn, attempts, rng, sleep):
    for attempt in range(attempts):
        try:
            return fn()
        except ConnectionError:
            if attempt == attempts - 1:
                raise
            sleep(backoff(attempt, rng=rng))
