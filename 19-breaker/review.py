"""가짜 시계와 가짜 리뷰 서비스. 실제로 기다리지 않고, 기다렸을 시간만 시계에 더한다."""


class Clock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def wait(self, seconds):
        self.now += seconds


class ReviewService:
    def __init__(self, clock, timeout=2.0):
        self.clock, self.timeout, self.down, self.calls = clock, timeout, False, 0

    def get(self):
        self.calls += 1
        if self.down:
            self.clock.wait(self.timeout)  # 답이 없어 타임아웃까지 붙잡혀 있다
            raise TimeoutError("리뷰 서비스 응답 없음")
        self.clock.wait(0.05)
        return "별점 4.6 (128개)"
