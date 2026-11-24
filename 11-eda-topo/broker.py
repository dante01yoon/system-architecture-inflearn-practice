"""브로커 토폴로지: 가운데 지휘자 없이, 토픽에 올린 이벤트를 구독자마다 한 부씩 나눠 준다."""
MAX_TRIES = 3


class Broker:
    def __init__(self):
        self.subs, self.trace, self.dead = {}, [], []

    def subscribe(self, topic, handler):
        self.subs.setdefault(topic, []).append(handler)

    def publish(self, topic, msg):
        for handler in self.subs.get(topic, []):  # Pub/Sub: 구독자마다 한 부씩
            self.trace.append(f"{topic} -> {handler.__name__}")
            self.deliver(topic, handler, dict(msg))

    def deliver(self, topic, handler, msg):
        for _ in range(MAX_TRIES):
            try:
                return handler(msg, self)
            except Exception as e:
                error = e
        self.dead.append((topic, handler.__name__, msg))  # Dead Letter Channel
        print(f"   {handler.__name__} {MAX_TRIES}번 실패({error}) -> DLQ")
