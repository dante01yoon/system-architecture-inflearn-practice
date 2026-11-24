"""python3 demo.py 1 → 흩어진 코드 세기 + 요청 id 로그,  2 → 미들웨어 순서와 예외 삼키기"""
import ast
import logging
import sys
from pathlib import Path

import after

HERE = Path(__file__).parent
HANDLERS = ("list_books", "place_order", "cancel_order")
CROSS = ("log.", "t0", "check_token(header):", "return 401", "try:", "except", "return 500")


def count(file):
    """핸들러 몸통 줄을 횡단 코드(로그·시간·인증·에러 처리)와 업무 코드로 나눠 센다."""
    src = (HERE / file).read_text(encoding="utf-8").splitlines()
    cross = biz = 0
    for f in ast.parse("\n".join(src)).body:
        if isinstance(f, ast.FunctionDef) and f.name in HANDLERS:
            for line in src[f.body[0].lineno - 1:f.end_lineno]:
                if line.strip():
                    if any(m in line for m in CROSS):
                        cross += 1
                    else:
                        biz += 1
    rid_args = sum(isinstance(f, ast.FunctionDef) and bool(f.args.args) and f.args.args[0].arg == "rid"
                   for f in ast.parse("\n".join(src)).body)
    return cross, biz, rid_args


def setup_log():
    h = logging.StreamHandler(sys.stdout)
    h.addFilter(after.AddRequestId())
    h.setFormatter(logging.Formatter("   rid=%(rid)s %(message)s"))
    after.log.handlers[:] = [h]
    after.log.setLevel(logging.INFO)
    after.log.propagate = False


def call(app, path, token="tok-demo-7f3a9c", book="ddia"):
    status = {}
    env = {"PATH_INFO": path, "HTTP_AUTHORIZATION": f"Bearer {token}", "book": book}
    app(env, lambda s, h: status.setdefault("s", s.split()[0]))
    return status["s"]


def one():
    c, b, r = count("before.py")
    print("1) 고치기 전 before.py · 핸들러 3개")
    print(f"   횡단 코드 {c}줄 · 업무 코드 {b}줄 · 요청 id를 인자로 받는 함수 {r}개")
    c, b, r = count("after.py")
    print("2) 고친 뒤 after.py · 핸들러 3개")
    print(f"   횡단 코드 {c}줄 · 업무 코드 {b}줄 · 요청 id를 인자로 받는 함수 {r}개")
    setup_log()
    app = after.make_app(after.with_request_id, after.errors, after.auth, after.access_log)
    print("3) 주문 요청 두 번 · 로그 맨 앞이 요청 id")
    for _ in range(2):
        call(app, "/orders")


def two():
    setup_log()
    print("1) 순서 잘못: 로그가 인증보다 바깥")
    bad = after.make_app(after.with_request_id, after.access_log, after.auth)
    call(bad, "/books")
    print("2) 고침: 인증이 로그보다 바깥")
    good = after.make_app(after.with_request_id, after.auth, after.access_log)
    call(good, "/books")

    def fail(user, amount):
        raise ConnectionError("결제 서버 응답 없음")
    after.charge = after.swallow(fail)
    print("3) 예외를 삼키는 데코레이터 · 결제 실패")
    app = after.make_app(after.with_request_id, after.errors, after.auth)
    print(f"   삼킴: 상태 {call(app, '/orders')}  ← 결제는 실패했는데 주문 완료")
    after.charge = fail
    print(f"   고침: 상태 {call(app, '/orders')}")


if __name__ == "__main__":
    {"1": one, "2": two}[sys.argv[1] if len(sys.argv) > 1 else "1"]()
