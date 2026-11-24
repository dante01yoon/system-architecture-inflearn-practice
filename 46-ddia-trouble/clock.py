"""믿을 수 없는 시계. 노드마다 벽시계가 조금씩 다르고, 동기화(NTP)가 시계를 되감기도 한다."""


class WallClock:
    """하루 중 시각(time.time 같은 것): 다른 노드와 비교하려고 쓰지만, 어긋나고 뒤로 갈 수 있다."""
    def __init__(self, skew=0):
        self.skew = skew                         # 실제 시각과의 차이(밀리초)

    def now(self, real):
        return real + self.skew

    def ntp_set(self, correction):
        self.skew += correction                  # 동기화가 시계를 앞뒤로 맞춤


class MonotonicClock:
    """단조 시계(time.monotonic 같은 것): 뒤로 가지 않는다. 한 노드 안에서 걸린 시간을 잴 때만 쓴다."""
    def __init__(self, start=12345):
        self.start = start                       # 기준점은 아무 의미 없음

    def now(self, real):
        return self.start + real


def lww_merge(writes):
    """last write wins: 도장(타임스탬프)이 가장 큰 쓰기 하나만 남긴다."""
    return max(writes, key=lambda w: w["stamp"])
