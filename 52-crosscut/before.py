"""고치기 전: 핸들러마다 로그·인증·시간 재기·에러 처리·요청 id를 직접 챙긴다."""
import logging
import time

log = logging.getLogger("before")
TOKENS = {"tok-demo-7f3a9c": "minji"}
STOCK = {"ddia": 3}


def check_token(header):
    return TOKENS.get(header.removeprefix("Bearer "))


def list_books(rid, header):
    t0 = time.perf_counter()
    log.info("rid=%s event=start path=/books", rid)
    if not check_token(header):
        return 401, None
    try:
        books = sorted(STOCK)
    except Exception:
        log.error("rid=%s event=error", rid)
        return 500, None
    log.info("rid=%s event=end ms=%.1f", rid, (time.perf_counter() - t0) * 1000)
    return 200, books


def place_order(rid, header, book):
    t0 = time.perf_counter()
    log.info("rid=%s event=start path=/orders", rid)
    if not check_token(header):
        return 401, None
    try:
        reserve_stock(rid, book)
        charge(rid, check_token(header), 36000)
    except Exception:
        log.error("rid=%s event=error", rid)
        return 500, None
    log.info("rid=%s event=end ms=%.1f", rid, (time.perf_counter() - t0) * 1000)
    return 201, book


def cancel_order(rid, header, book):
    t0 = time.perf_counter()
    log.info("rid=%s event=start path=/cancel", rid)
    if not check_token(header):
        return 401, None
    try:
        STOCK[book] += 1
    except Exception:
        log.error("rid=%s event=error", rid)
        return 500, None
    log.info("rid=%s event=end ms=%.1f", rid, (time.perf_counter() - t0) * 1000)
    return 200, book


def reserve_stock(rid, book):
    log.info("rid=%s event=reserve book=%s", rid, book)
    STOCK[book] -= 1


def charge(rid, user, amount):
    log.info("rid=%s event=charge user=%s amount=%d", rid, user, amount)
