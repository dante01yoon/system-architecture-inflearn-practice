"""서점 10분치 지표(가정). 5분째(300초)부터 외부 결제 API가 느려진다(0.2초 → 2.4초).
/checkout만 DB 연결을 쥔 채 결제를 기다리고, 나머지는 캐시에서 답한다."""
import math
import random

POOL = 20          # DB 연결 풀 크기
TIMEOUT = 3.0      # 연결을 3초 넘게 못 받으면 실패
# 엔드포인트: (초당 요청, 응답 시간 중앙값 초)
ENDPOINTS = {"/books": (52, 0.040), "/search": (20, 0.080), "/cart": (12, 0.025)}


def checkout(rnd, pay, work, hold_while_paying=True):
    """1초 동안의 결제 요청. work = 밀린 연결 사용량(연결·초)."""
    reqs, waited, failed = [], 0, 0
    for _ in range(rnd.randint(7, 11)):
        paying = rnd.lognormvariate(math.log(pay), 0.25)    # 결제 API 응답
        hold = 0.03 + (paying if hold_while_paying else 0)  # 연결을 쥐는 시간
        wait = max(0.0, work - POOL) / POOL                  # 풀이 차면 줄 서기
        if wait > TIMEOUT:
            reqs.append(("/checkout", TIMEOUT, True))
            failed += 1
            continue
        waited += wait > 0
        work += hold
        reqs.append(("/checkout", wait + 0.03 + paying, False))
    return reqs, work, waited, failed


def seconds(seed=3, hold_while_paying=True):
    """600초 동안 초마다 (요청 목록, 자원 표본 {자원: (사용률 %, 포화, 오류)})."""
    rnd = random.Random(seed)
    out, work = [], 0.0
    for t in range(600):
        reqs = [(ep, rnd.lognormvariate(math.log(med), 0.3), rnd.random() < 0.001)
                for ep, (rate, med) in ENDPOINTS.items()
                for _ in range(rnd.randint(rate - 2, rate + 2))]
        pay = 2.4 if t >= 300 else 0.2
        more, work, waited, failed = checkout(rnd, pay, work, hold_while_paying)
        out.append((reqs + more, {
            "앱 CPU": (rnd.gauss(34, 4), 0, 0), "앱 메모리": (rnd.gauss(61, 1), 0, 0),
            "네트워크": (rnd.gauss(12, 2), 0, 0), "DB CPU": (rnd.gauss(18, 3), 0, 0),
            "DB 디스크": (rnd.gauss(22, 3), 0, 0),
            "DB 연결 풀": (min(work, POOL) / POOL * 100, waited, failed),
        }))
        work = max(0.0, work - POOL)     # 1초 동안 연결 20개가 일한 만큼 줄어든다
    return out
