"""한 프로세스 안의 작은 이벤트 버스: 토픽마다 구독자, 올라온 순서대로 하나씩 배달."""
from collections import deque


class Bus:
    def __init__(self):
        self.subs, self.queue, self.trace = {}, deque(), []

    def subscribe(self, topic, handler):
        self.subs.setdefault(topic, []).append(handler)

    def publish(self, topic, msg):
        self.queue.append((topic, msg))       # 바로 부르지 않고 줄에 넣는다

    def run(self):
        while self.queue:
            topic, msg = self.queue.popleft()
            for h in self.subs.get(topic, []):
                self.trace.append(f"{topic} -> {type(getattr(h, '__self__', h)).__name__}")
                h(dict(msg))                  # 구독자마다 한 부씩
