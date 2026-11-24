"""서점 요청 로그 1시간(가정). 26~29분 DB가 조금씩 느려짐, 30~39분 DB 느림 장애,
40~44분 DB 연결 끊김, 45분부터 회복."""
import math
import random

RAMP = {26: 80, 27: 150, 28: 250, 29: 330}   # 장애 직전 성공 응답 중앙값(ms)


def minute(m, rnd):
    """m분의 요청 목록 [(지연 ms, 상태 코드, 내용 정상?)]."""
    if 30 <= m < 40:     # DB 느림: 요청 수, 중앙값, 퍼짐, 실패율, 빈 결과율
        n, med, sd, err, empty = 1850, 550, 0.55, 0.04, 0.03
    elif 40 <= m < 45:   # DB 연결 끊김: 대부분 곧바로 500
        n, med, sd, err, empty = 2400, 40, 0.4, 0.85, 0.003
    else:                # 평소(장애 직전이면 점점 느려짐)
        n, med, sd, err, empty = 2160, RAMP.get(m, 40), 0.4, 0.001, 0.003
    out = []
    for _ in range(int(n * rnd.uniform(0.96, 1.04))):
        if rnd.random() < err:
            # 연결이 없으면 곧바로 실패, 풀을 기다리면 1초 뒤 실패
            ms = rnd.lognormvariate(math.log(4), 0.3) if m >= 40 else 1000.0
            out.append((ms, 500, False))
        else:
            ms = rnd.lognormvariate(math.log(med), sd)
            out.append((ms, 200, rnd.random() >= empty))
    return out


def hour(seed=7):
    """60분치 로그: 분마다 요청 목록."""
    rnd = random.Random(seed)
    return [minute(m, rnd) for m in range(60)]
