"""메시지 큐: 소비자가 받아 가서 ack하면 지운다. ack 전에 소비자가 죽으면 다시 보낸다."""


class Queue:
    def __init__(self, messages):
        self.ready, self.unacked = list(messages), {}

    def receive(self, auto_ack):
        msg = self.ready.pop(0)            # 최대 한 번: 받는 순간 큐에서 사라진다
        if not auto_ack:                   # 최소 한 번: ack할 때까지 붙잡아 둔다
            self.unacked[msg["id"]] = msg
        return msg

    def ack(self, msg):
        del self.unacked[msg["id"]]

    def consumer_died(self):
        self.ready[:0] = self.unacked.values()  # ack 못 받은 것을 줄 맨 앞에 다시
        self.unacked.clear()
