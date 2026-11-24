"""카탈로그 서비스: 책 값을 알려 준다. 버전 2는 10% 할인."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

PRICES = {"Clean Architecture": 32000, "Release It!": 30000}


def price(book, version):
    return PRICES[book] * 9 // 10 if version == 2 else PRICES[book]


def catalog_server(port, version):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            book = parse_qs(urlparse(self.path).query)["book"][0]
            reply(self, 200, {"price": price(book, version), "version": version})

        def log_message(self, *args):  # 요청마다 찍는 기본 로그는 끈다
            pass

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def reply(handler, status, data):
    body = json.dumps(data, ensure_ascii=False).encode()
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.end_headers()
    handler.wfile.write(body)
