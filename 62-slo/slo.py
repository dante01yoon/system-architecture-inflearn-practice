"""서점 결제 30일 기록으로 SLI·SLO·에러 버짓·소진 속도·다중 창 경보를 계산한다."""
import random

SLO = 0.999                 # 결제 가용성 목표 99.9%, 창 30일
DAYS, MIN = 30, 1440        # 30일 × 하루 1,440분
# SRE Workbook 「Alerting on SLOs」 표의 호출(page) 두 줄: (긴 창 분, 짧은 창 분, 소진 속도)
PAGE = [(60, 5, 14.4), (360, 30, 6)]


def month(seed=7, incident=None):
    """분마다 (전체 요청, 4xx, 5xx). incident=(시작 분, 길이 분, 실패 비율)."""
    # shortcut: 요청 하나하나 대신 분 단위 합계, 분당 90~110건으로 고르다고 가정
    rng = random.Random(seed)
    rows = []
    for m in range(DAYS * MIN):
        total = rng.randint(90, 110)
        client = max(0, int(rng.gauss(2, 1)))   # 4xx: 손님 실수
        server = 1 if rng.random() < (total - client) * 0.0003 else 0  # 평소 약 0.03%
        if incident and incident[0] <= m < incident[0] + incident[1]:
            server = round((total - client) * incident[2])
        rows.append((total, client, server))
    return rows


def sli(rows):
    """SLI = 좋은 요청 / 유효한 요청."""
    valid = sum(t - c for t, c, _ in rows)
    good = valid - sum(s for _, _, s in rows)
    return good, valid


def budget(rows):
    """에러 버짓 = (1 − SLO) × 유효 요청. 돌려주는 값: (허용 실패, 쓴 실패)."""
    good, valid = sli(rows)
    return (1 - SLO) * valid, valid - good


def burn(rows, end, minutes):
    """최근 minutes분의 실패 비율 / (1 − SLO). 1이면 30일 끝에 예산을 딱 다 쓴다."""
    good, valid = sli(rows[max(0, end - minutes):end])
    return (valid - good) / valid / (1 - SLO) if valid else 0.0


def alerts(rows):
    """다중 창 경보: 긴 창과 짧은 창이 둘 다 넘을 때만. 바뀐 순간만 [(분, 켜짐?, 이유)]."""
    V, B = [0], [0]  # 누적 합(창마다 다시 더하지 않게)
    for t, c, s in rows:
        V.append(V[-1] + t - c); B.append(B[-1] + s)

    def rate(m, w):
        a = max(0, m - w)
        return (B[m] - B[a]) / (V[m] - V[a]) / (1 - SLO)

    out, on = [], False
    for m in range(1, len(rows) + 1):
        why = None
        for lw, sw, k in PAGE:
            if m >= lw and rate(m, lw) >= k and rate(m, sw) >= k:  # 긴 창이 다 찬 뒤부터
                why = f"{lw // 60}시간 {rate(m, lw):.1f}배 · {sw}분 {rate(m, sw):.1f}배"
                break
        if bool(why) != on:
            on = bool(why)
            out.append((m, on, why))
    return out


def clock(m):
    d, r = divmod(m, MIN)
    return f"{d + 1}일 {r // 60:02d}:{r % 60:02d}"
