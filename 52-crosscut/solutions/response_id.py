"""연습 문제 풀이: 요청 id를 응답 헤더 X-Request-Id로 돌려주는 미들웨어. python3 solutions/response_id.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import after  # noqa: E402


def response_id(app):
    def mw(environ, start_response):
        def sr(status, headers):
            return start_response(status, headers + [("X-Request-Id", after.request_id.get())])
        return app(environ, sr)
    return mw


if __name__ == "__main__":
    # with_request_id 안쪽에 둬야 id가 이미 정해져 있다 — 순서가 또 중요하다
    app = after.make_app(after.with_request_id, response_id, after.auth)
    env = {"PATH_INFO": "/books", "HTTP_AUTHORIZATION": "Bearer tok-demo-7f3a9c"}
    app(env, lambda s, h: print(s, h))
