"""가짜 리뷰 서비스와 주문 서비스. 리뷰는 느려질 수 있다(실제로 그만큼 잠든다)."""
import time


class Review:
    def __init__(self):
        self.slow = False

    def get(self):
        time.sleep(1.0 if self.slow else 0.01)  # 느려지면 답이 1초 뒤에 온다
        return "별점 4.6"


def place_order(n):
    time.sleep(0.01)
    return f"주문 #{n} 접수"
