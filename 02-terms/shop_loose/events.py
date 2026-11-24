"""이벤트 게시판: 모두가 기대는 공용 약속."""
handlers = {}


def subscribe(name, handler):
    handlers.setdefault(name, []).append(handler)


def publish(name, data):
    for handler in handlers.get(name, []):
        handler(data)
