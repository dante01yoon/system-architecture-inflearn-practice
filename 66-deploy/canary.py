"""롤링 카나리 시뮬레이션(가정한 숫자). 인스턴스 20대를 v1 → v2로 1 · 5 · 10 · 20대씩 바꾸고,
단계마다 10분 지켜본 뒤 v2 몫의 오류율로 판정한다. /checkout은 분당 100건(SLO 수업의 서점)."""
import random

SLO = 99.9            # 가용성 목표 %
PAGE = 14.4           # v2 몫이 이 배수로 예산을 태우면 되돌림
BUDGET_30D = 4252     # 30일 오류 예산(SLO 수업 실측: 유효 4,252,340건 × 0.1%)
PER_MIN, WATCH, FLEET = 100, 10, 20
STEPS = [1, 5, 10, 20]   # v2 인스턴스 수 → 5% · 25% · 50% · 100%


def requests(rnd, n, fail):
    """n건 중 실패 수."""
    return sum(rnd.random() < fail for _ in range(n))


def rollout(v2_fail, v1_fail=0.0003, seed=10):
    """단계마다 (v2 몫 %, v2 요청, v2 오류, v1 오류율 %, v2 소진 속도, 판정)."""
    rnd, rows = random.Random(seed), []
    for n in STEPS:
        total = PER_MIN * WATCH
        new = total * n // FLEET
        bad_new, bad_old = requests(rnd, new, v2_fail), requests(rnd, total - new, v1_fail)
        rate = bad_new / new * 100
        speed = rate / (100 - SLO)
        verdict = "되돌림" if speed >= PAGE else ("완료" if n == FLEET else "다음")
        old_rate = bad_old / max(total - new, 1) * 100
        rows.append((n * 100 // FLEET, new, bad_new, old_rate, speed, verdict))
        if verdict == "되돌림":
            break
    return rows


def big_bang(v2_fail, seed=10):
    """카나리 없이 한 번에 100%로 내보내고 같은 10분 뒤에 알아챘다면 생긴 오류 수."""
    return requests(random.Random(seed), PER_MIN * WATCH, v2_fail)
