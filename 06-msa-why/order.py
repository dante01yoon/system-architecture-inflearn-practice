"""주문 서비스: 카탈로그에 값을 물어 합계를 낸다. 카탈로그가 없으면 마지막으로 본 값을 쓴다."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, quote, urlparse
from urllib.request import urlopen

from catalog import reply


def order_server(port, catalog_url):
    seen = {"orders": 0, "price": {}}  # 받은 주문 수, 책마다 마지막으로 본 값

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            q = parse_qs(urlparse(self.path).query)
            book, qty = q["book"][0], int(q["qty"][0])
            seen["orders"] += 1
            try:
                with urlopen(f"{catalog_url}/price?book={quote(book)}", timeout=0.5) as r:
                    info = json.load(r)
                seen["price"][book] = info["price"]
                note = f"catalog v{info['version']}"
            except OSError:  # 카탈로그가 내려가 있다
                if book not in seen["price"]:
                    return reply(self, 503, {"error": "카탈로그 응답 없음"})
                note = "저장해 둔 값"
            total = seen["price"][book] * qty
            reply(self, 200, {"total": total, "note": note, "orders": seen["orders"]})

        def log_message(self, *args):
            pass

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)
