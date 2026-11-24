"""연습 풀이: 가격 이벤트(PriceChanged)를 더하고 「수요일 오후 가격」을 묻는다. 기존 이벤트는 손대지 않는다."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from stock import apply as base_apply  # noqa: E402
from store import EventStore  # noqa: E402


def apply(state, type, data):
    if type == "PriceChanged":
        return {**state, "price": data["price"]}
    return base_apply(state, type, data)


def rebuild(events):
    state = {"stock": 0, "sold": 0, "price": None}
    for _, type, _, data, _ in events:
        state = apply(state, type, data)
    return state


if __name__ == "__main__":
    s = EventStore()
    v = s.append("b", 0, "PriceChanged", {"price": 32000}, "2026-11-09")
    v = s.append("b", v, "StockReceived", {"qty": 10}, "2026-11-09")
    s.append("b", v, "PriceChanged", {"price": 28800}, "2026-11-12")
    wed = rebuild(s.read("b", until_day="2026-11-11"))
    assert wed["price"] == 32000 and rebuild(s.read("b"))["price"] == 28800
    print("수요일 가격", wed["price"], "/ 지금 가격", rebuild(s.read("b"))["price"])
