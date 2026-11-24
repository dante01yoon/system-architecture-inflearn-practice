"""책 재고: 이벤트를 차례로 적용해 지금 상태를 만든다. 상태는 저장하지 않는다."""

EMPTY = {"stock": 0, "sold": 0}


def upcast(type, schema, data):
    """옛 모양(스키마 1) 이벤트를 지금 모양(스키마 2)으로. 저장된 이벤트는 그대로 둔다."""
    if type == "BookSold" and schema == 1:
        return {"qty": data["count"], "order": None}  # 옛 모양: 권수가 count, 주문 번호 없음
    return data


def apply(state, type, data):
    if type == "StockReceived":
        return {**state, "stock": state["stock"] + data["qty"]}
    if type == "BookSold":
        return {"stock": state["stock"] - data["qty"], "sold": state["sold"] + data["qty"]}
    if type == "BookReturned":
        return {"stock": state["stock"] + data["qty"], "sold": state["sold"] - data["qty"]}
    return state  # 모르는 이벤트는 건너뛴다


def rebuild(events, state=None):
    state = dict(state or EMPTY)
    for version, type, schema, data, day in events:
        state = apply(state, type, upcast(type, schema, data))
    return state


def load(store, stream):
    """마지막 스냅숏에서 시작해, 그 뒤 이벤트만 적용한다."""
    version, snap = store.last_snapshot(stream)
    events = store.read(stream, after=version)
    return rebuild(events, snap), version, len(events)


def sales_by_day(events):
    """프로젝션: 같은 이벤트로 만든 또 하나의 읽기 모델(날짜별 판매 권수)."""
    out = {}
    for version, type, schema, data, day in events:
        if type == "BookSold":
            out[day] = out.get(day, 0) + upcast(type, schema, data)["qty"]
    return out
