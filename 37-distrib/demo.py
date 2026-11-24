"""서점을 여러 대로 나눌까? 1 = 용량, 2 = 가용성, 3 = 거리."""
import sys
import unicodedata

from calc import RTT, TRIPS, availability, downtime_hours, machines, nearest, page_wait

PEAK, PER_APP, BIGGEST = 20_000, 2_000, 8_000   # 초당 요청: 최고 부하, 보통 서버 한 대, 가장 큰 서버 한 대


def pad(text, width):
    """한글은 두 칸으로 세어 오른쪽을 채운다(표 줄 맞춤)."""
    return text + ' ' * (width - sum(2 if unicodedata.east_asian_width(c) in 'WF' else 1 for c in text))


def capacity():
    print(f"1) 용량 · 최고 부하 초당 {PEAK:,}건 (가정)")
    print(f"   가장 큰 서버 한 대: 초당 {BIGGEST:,}건 → 모자람 {PEAK - BIGGEST:,}건")
    print(f"   보통 서버(초당 {PER_APP:,}건) × {machines(PEAK, PER_APP, 0)}대 = 딱 맞음")
    print(f"   여유 30%를 남기면 {machines(PEAK, PER_APP)}대 · 대신 일을 나눠 줄 앞단이 필요")


def avail():
    each = 0.995
    print(f"2) 가용성 · 서버 한 대가 살아 있는 비율 {each:.1%} (가정, 서로 따로 고장)")
    for n in (1, 2, 3):
        a = availability(each, n)
        h = downtime_hours(a)
        down = f"{h:.1f}시간" if h >= 1 else f"{h * 60:.1f}분" if h * 60 >= 1 else f"{h * 3600:.2f}초"
        print(f"   복제본 {n}개: {f'{a * 100:.7f}'.rstrip('0')}% · 1년에 멈추는 시간 약 {down}")
    print("   대신 쓸 때마다 복제본끼리 맞춰야 함")


def distance():
    print(f"3) 거리 · 페이지 하나 = 왕복 {TRIPS}번 (가정한 왕복 시간)")
    print(f"   {pad('손님', 12)}{pad('서울 한 곳', 14)}가까운 곳")
    for user in RTT:
        one, near = page_wait(user, '서울'), page_wait(user, nearest(user))
        print(f"   {pad(user, 12)}{pad(f'{one}ms', 14)}{near}ms ({nearest(user)})")
    print(f"   주문을 서울·미국 동부 둘 다에 확정하면 +{RTT['서울']['미국 동부']}ms")


if __name__ == "__main__":
    {'1': capacity, '2': avail, '3': distance}.get(sys.argv[1] if len(sys.argv) > 1 else '1')()
