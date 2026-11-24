"""고친 뒤: 횡단 관심사는 한 곳에 — WSGI 미들웨어 줄, 데코레이터, contextvars 요청 id."""
import contextlib
import contextvars
import functools
import itertools
import logging
import time

request_id = contextvars.ContextVar("request_id", default="-")
log = logging.getLogger("shop")
TOKENS = {"tok-demo-7f3a9c": "minji"}
STOCK = {"ddia": 3}
_ids = itertools.count(1)


class AddRequestId(logging.Filter):
    def filter(self, record):
        record.rid = request_id.get()      # 로그 한 줄마다 지금 요청의 id
        return True


def with_request_id(app):
    def mw(environ, start_response):
        token = request_id.set(f"r-{next(_ids):04d}")
        try:
            return app(environ, start_response)
        finally:
            request_id.reset(token)
    return mw


def access_log(app):
    def mw(environ, start_response):
        t0, seen = time.perf_counter(), {}
        auth_header = environ.get("HTTP_AUTHORIZATION", "-")
        log.info("event=start path=%s auth=%s", environ["PATH_INFO"], auth_header)

        def sr(status, headers):
            seen["status"] = status.split()[0]
            return start_response(status, headers)
        body = app(environ, sr)
        ms = (time.perf_counter() - t0) * 1000
        log.info("event=end status=%s ms=%.1f", seen.get("status"), ms)
        return body
    return mw


def auth(app):
    def mw(environ, start_response):
        raw = environ.get("HTTP_AUTHORIZATION", "")
        user = TOKENS.get(raw.removeprefix("Bearer "))
        if not user:
            start_response("401 Unauthorized", [])
            return [b""]
        environ["HTTP_AUTHORIZATION"] = "Bearer ****" + raw[-2:]  # 원문을 가린다
        environ["user"] = user
        return app(environ, start_response)
    return mw


def errors(app):
    def mw(environ, start_response):
        try:
            return app(environ, start_response)
        except Exception as e:
            log.error("event=error type=%s", type(e).__name__)
            start_response("500 Internal Server Error", [])
            return [b""]
    return mw


def chain(app, *middlewares):
    """chain(app, a, b, c) = a(b(c(app))) — 앞에 적은 것이 바깥(먼저 받는다)."""
    for mw in reversed(middlewares):
        app = mw(app)
    return app


@contextlib.contextmanager
def span(name):
    t0 = time.perf_counter()
    try:
        yield                              # with 블록 안의 코드가 여기서 돈다
    finally:
        ms = (time.perf_counter() - t0) * 1000
        log.info("event=timing fn=%s ms=%.1f", name, ms)


def timed(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        with span(fn.__name__):
            return fn(*args, **kwargs)
    return wrapper


def swallow(fn):
    """나쁜 예: 모든 예외를 삼킨다 — 실패가 성공처럼 보인다."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception:
            return None
    return wrapper


# ── 업무 코드: 횡단 관심사가 한 줄도 없다 ──
def list_books(environ, start_response):
    start_response("200 OK", [])
    return [", ".join(sorted(STOCK)).encode()]


def place_order(environ, start_response):
    reserve_stock(environ["book"])
    charge(environ["user"], 36000)
    start_response("201 Created", [])
    return [environ["book"].encode()]


def cancel_order(environ, start_response):
    STOCK[environ["book"]] += 1
    start_response("200 OK", [])
    return [environ["book"].encode()]


@timed
def reserve_stock(book):
    log.info("event=reserve book=%s", book)
    STOCK[book] -= 1


def charge(user, amount):
    log.info("event=charge user=%s amount=%d", user, amount)


ROUTES = {"/books": list_books, "/orders": place_order, "/cancel": cancel_order}


def router(environ, start_response):
    return ROUTES[environ["PATH_INFO"]](environ, start_response)


def make_app(*middlewares):
    return chain(router, *middlewares)
