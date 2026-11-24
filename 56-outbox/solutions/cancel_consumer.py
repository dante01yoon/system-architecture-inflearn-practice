"""연습 풀이: 취소 이벤트를 받으면 예약을 풀고, 같은 취소가 두 번 와도 한 번만 반영한다."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from outbox import Consumer, PollingRelay, cancel, open_db, place  # noqa: E402


class StockConsumer(Consumer):
    def handle(self, event):
        if event["id"] in self.seen:
            return "중복 무시"
        self.seen.add(event["id"])
        step = -1 if event["type"] == "OrderCancelled" else 1
        self.reserved[event["book"]] = self.reserved.get(event["book"], 0) + step
        return "처리"


if __name__ == "__main__":
    db, broker = open_db(), []
    place(db, 1, "DDIA"); cancel(db, 1)
    PollingRelay(db, broker).run()
    broker.append(broker[-1])  # 취소 이벤트가 한 번 더 옴
    stock = StockConsumer()
    for e in broker:
        print(e["id"], "→", stock.handle(e))
    print("DDIA 예약:", stock.reserved["DDIA"])
    assert stock.reserved["DDIA"] == 0
