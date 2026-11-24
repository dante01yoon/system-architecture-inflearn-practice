"""API 게이트웨이: 문 하나. 인증 확인 → 경로 보고 서비스로 보내기(라우팅) → 책 화면은 셋을 모아 한 번에(집계)."""
import json
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.request import urlopen

ROUTES = {"/catalog/": 8811, "/reviews/": 8812, "/stock/": 8813}
TOKEN = "Bearer demo-token"
pool = ThreadPoolExecutor(8)


def fetch(port, path):
    try:
        with urlopen(f"http://127.0.0.1:{port}{path}", timeout=1) as r:
            return json.load(r)
    except OSError:
        return None  # 한 서비스가 죽어도 화면 전체를 깨지 않는다


def book_page(isbn):
    parts = {k.strip("/"): pool.submit(fetch, p, f"{k}{isbn}") for k, p in ROUTES.items()}
    return {name: f.result() for name, f in parts.items()}


class Gateway(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.headers.get("Authorization") != TOKEN:
            return self.reply(401, {"error": "로그인이 필요해요"})
        if self.path.startswith("/book-page/"):
            return self.reply(200, book_page(self.path.rsplit("/", 1)[-1]))
        for prefix, port in ROUTES.items():
            if self.path.startswith(prefix):
                return self.reply(200, fetch(port, self.path))
        self.reply(404, {"error": "없는 경로"})

    def reply(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def start(port=8814):
    server = ThreadingHTTPServer(("127.0.0.1", port), Gateway)
    Thread(target=server.serve_forever, daemon=True).start()
    return server
