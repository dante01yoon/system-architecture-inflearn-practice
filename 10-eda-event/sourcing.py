"""이벤트 소싱 맛보기: 바뀐 기록(이벤트)을 처음부터 다시 적용해 지금 상태를 만든다."""

EVENTS = [
    {"type": "OrderPlaced", "books": {"Clean Architecture": 1}},
    {"type": "BookAdded", "book": "DDIA", "qty": 2},
    {"type": "OrderPaid", "amount": 96000},
]


def apply(state, e):
    if e["type"] == "OrderPlaced":
        return {"status": "placed", "books": dict(e["books"])}
    if e["type"] == "BookAdded":
        return {**state, "books": {**state["books"], e["book"]: e["qty"]}}
    if e["type"] == "OrderPaid":
        return {**state, "status": "paid", "paid": e["amount"]}
    return state


def replay(events):
    state = {}
    for e in events:
        state = apply(state, e)
    return state
