"""서점 20분치 분 단위 숫자(가정한 값). 8분째부터 외부 결제 API가 느려지고(0.2초 → 2.4초),
/checkout이 DB 연결을 쥔 채 결제를 기다려서 연결 풀이 찬다(S4-03과 같은 장애)."""
# 다른 서비스: (초당 요청, 오류율 %, p99 ms) · 다른 자원: 사용률 % (줄·오류 0)
SVC = {"/books": (52, 0.1, 81), "/search": (20, 0.1, 158), "/cart": (12, 0.1, 49)}
RES = {"앱 CPU": 34, "앱 메모리": 61, "네트워크": 12, "DB CPU": 18, "DB 디스크": 22}
# /checkout 분마다: (p99 ms, 오류율 %, 1초 넘은 %, 연결 풀 사용률 %, 줄 선 요청, 시간 초과)
NORMAL = (395, 0.0, 0, 10, 0.0, 0)
BAD = {8: (1780, 0.0, 90, 78, 0.0, 0), 9: (3050, 0.6, 100, 100, 2.4, 3),
       10: (3380, 4.8, 100, 100, 6.1, 26), 11: (3430, 9.6, 100, 100, 7.6, 52)}


def minutes(n=20):
    """분마다 {"svc": {서비스: (R, E, D)}, "res": {자원: (U, S, E)}, "slow": 1초 넘은 %}."""
    log = []
    for t in range(n):
        d, e, slow, u, s, err = BAD.get(min(t, 11), NORMAL) if t >= 8 else NORMAL
        svc = dict(SVC, **{"/checkout": (9, e, d)})
        res = {k: (v, 0.0, 0) for k, v in RES.items()}
        res["DB 연결 풀"] = (u, s, err)
        log.append({"svc": svc, "res": res, "slow": slow})
    return log
