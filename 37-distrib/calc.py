"""분산을 할지 정하는 세 가지 계산: 용량, 가용성, 거리. 숫자는 모두 설명을 위해 정한 가정이다."""
import math

HOURS = 365 * 24


def machines(peak, per_machine, headroom=0.3):
    """최고 부하를 견디려면 몇 대가 필요한가(여유 몫을 남기고)."""
    return math.ceil(peak / (per_machine * (1 - headroom)))


def availability(each, copies):
    """복제본 copies개 중 하나만 살아 있어도 된다면. 서로 따로 고장 난다고 가정한다."""
    return 1 - (1 - each) ** copies


def downtime_hours(avail):
    return (1 - avail) * HOURS


RTT = {   # 왕복 시간(ms), 가정한 값
    '서울': {'서울': 5, '미국 동부': 180, '유럽': 240},
    '미국 동부': {'서울': 180, '미국 동부': 10, '유럽': 90},
    '유럽': {'서울': 240, '미국 동부': 90, '유럽': 10},
}
TRIPS = 4    # 페이지 하나에 오가는 횟수(연결 · 암호화 · 요청), 가정


def page_wait(user, region):
    return RTT[user][region] * TRIPS


def nearest(user):
    return min(RTT[user], key=RTT[user].get)
