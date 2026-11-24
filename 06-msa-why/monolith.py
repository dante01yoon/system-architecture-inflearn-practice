"""모놀리스: 주문과 값 계산이 한 프로세스 안의 함수 호출."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from catalog import price, reply


def monolith_server(port, version):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            q = parse_qs(urlparse(self.path).query)
            book, qty = q["book"][0], int(q["qty"][0])
            total = price(book, version) * qty  # 네트워크 없이 바로 부른다
            reply(self, 200, {"total": total, "note": f"monolith v{version}"})

        def log_message(self, *args):
            pass

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)
