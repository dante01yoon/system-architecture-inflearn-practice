"""서점 서비스 셋(카탈로그·리뷰·재고). 각자 자기 포트에서 JSON 하나만 돌려준다. 인증은 모른다."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

BOOKS = {"9780134494166": "Clean Architecture"}
DATA = {
    "catalog": lambda isbn: {"title": BOOKS[isbn], "price": 32000},
    "reviews": lambda isbn: {"stars": 4.6, "count": 128},
    "stock": lambda isbn: {"left": 3},
}
PORTS = {"catalog": 8811, "reviews": 8812, "stock": 8813}


def make_handler(name):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            isbn = self.path.rsplit("/", 1)[-1]
            if isbn not in BOOKS:
                return self.send_error(404)
            body = json.dumps(DATA[name](isbn)).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):  # 터미널을 조용하게
            pass

    return Handler


def start(name, port=None):
    server = ThreadingHTTPServer(("127.0.0.1", port or PORTS[name]), make_handler(name))
    Thread(target=server.serve_forever, daemon=True).start()
    return server
