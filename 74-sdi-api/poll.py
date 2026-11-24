"""알림이 언제 올지 모를 때: 짧은 폴링 대 롱 폴링. 실제로 기다리지 않고 시간을 계산으로 흉내 낸다."""
import math
import random


def arrivals(n, horizon, seed=7):
    rnd = random.Random(seed)
    return sorted(rnd.uniform(0, horizon) for _ in range(n))


def short_poll(times, every, horizon):
    """every초마다 묻는다 → (요청 수, 빈 응답 수, 평균 지연 초)."""
    got = [math.ceil(t / every) * every for t in times]       # 도착한 뒤 첫 질문에 받는다
    requests = int(horizon // every)
    return requests, requests - len(set(got)), sum(g - t for g, t in zip(got, times)) / len(times)


def long_poll(times, hold, horizon, rtt=0.2):
    """서버가 알림이 올 때까지 최대 hold초 붙잡는다. 답을 받으면 rtt초 뒤 다시 묻는다."""
    t, i, requests, empty, delay = 0.0, 0, 0, 0, 0.0
    while t < horizon:
        requests += 1
        if i < len(times) and times[i] <= t + hold:
            done = max(t, times[i])                           # 알림이 오는 순간 답한다
            while i < len(times) and times[i] <= done:
                delay += done - times[i]
                i += 1
            t = done + rtt
        else:
            empty += 1                                        # 아무 일 없이 hold초가 지남
            t += hold
    return requests, empty, delay / max(len(times), 1)
