"""반짝 할인 2,000건을 세 가지 방법으로 받아 본다."""
import sys

from sim import N, SERVICE, SPAN, WORKERS, queue_length, simulate

RATE = WORKERS / SERVICE    # 초당 처리량 100건
MAX_WAIT = 3.0              # 손님이 기다려 줄 만한 시간(정한 값)
LIMIT = int(RATE * MAX_WAIT)  # Little의 법칙 L = λW


def main(part=""):
    # 녹화 터미널은 19줄 — 1은 위 두 줄과 1)~3), 2는 줄 길이 표(인자 없으면 전부)
    direct, queued, shed = simulate(0), simulate(None), simulate(LIMIT)
    if part != "2":
        summary(direct, queued, shed)
    if part != "1":
        table(queued, shed)


def summary(direct, queued, shed):
    print(f"반짝 할인: {SPAN:.0f}초 동안 주문 {N:,}건 (초당 {N / SPAN:.0f}건), DB는 초당 {RATE:.0f}건 · seed 2026")
    print(f"Little의 법칙 L = λW: 일꾼 = {RATE:.0f}건/초 × {SERVICE}초 = {WORKERS}명 · 줄 한도 = {RATE:.0f}건/초 × {MAX_WAIT:.0f}초 = {LIMIT}칸")
    print("1) 큐 없이 바로 DB로")
    print(f"   성공 {direct['done']:,} · DB 과부하 오류 {direct['rejected']:,}")
    print(f"2) 큐 + 일꾼 {WORKERS}명")
    print(f"   성공 {queued['done']:,} · 오류 {queued['rejected']} · 최대 대기 {queued['max_wait']:.1f}초 · 다 끝난 시각 {queued['end']:.1f}초")
    print(f"3) 줄 한도 {LIMIT}칸 + 부하 차단")
    print(f"   성공 {shed['done']:,} · 「잠시 후 다시」 {shed['rejected']:,} · 최대 대기 {shed['max_wait']:.1f}초")


def table(queued, shed):
    print("줄 길이   (2) 큐만 · # 하나 = 50건                (3) 한도 300")
    for t in range(0, 22, 2):
        q2, q3 = queue_length(queued['starts'], t), queue_length(shed['starts'], t)
        print(f"  {t:2}초  {'#' * round(q2 / 50):<22} {q2:5}     {q3:5}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
