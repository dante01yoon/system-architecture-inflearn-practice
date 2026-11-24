"""서점 REST API — 책 목록(offset · cursor), 위시리스트 PUT, 주문 POST. 표준 라이브러리 http.server만."""
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

PORT = 8921
STATE = {}


def reset():
    STATE.update(books=list(range(1, 51)), wishlist=set(), orders=[], keys={})


def newest_first():
    return sorted(STATE["books"], reverse=True)          # 번호가 클수록 새 책


def page_offset(offset, limit):
    return newest_first()[offset:offset + limit]


def page_cursor(cursor, limit):
    rows = [b for b in newest_first() if cursor is None or b < cursor][:limit]
    return rows, (rows[-1] if len(rows) == limit else None)   # 다음 쪽 커서 = 마지막으로 준 책


class Handler(BaseHTTPRequestHandler):
    def send(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        if u.path != "/v1/books":
            return self.send(404, {"error": "not found"})
        limit = int(q.get("limit", 5))
        if "offset" in q:
            return self.send(200, {"items": page_offset(int(q["offset"]), limit)})
        rows, nxt = page_cursor(int(q["cursor"]) if "cursor" in q else None, limit)
        self.send(200, {"items": rows, "next_cursor": nxt})

    def do_PUT(self):                              # PUT /v1/wishlist/7 — 「7번이 목록에 있다」로 만든다
        part = self.path.split("/")
        if part[1:3] != ["v1", "wishlist"] or not part[3].isdigit():
            return self.send(404, {"error": "not found"})
        STATE["wishlist"].add(int(part[3]))
        self.send(200, {"wishlist": sorted(STATE["wishlist"])})

    def do_POST(self):
        if self.path == "/v1/books":               # 새 책 하나를 만든다
            STATE["books"].append(max(STATE["books"]) + 1)
            return self.send(201, {"id": max(STATE["books"])})
        if self.path != "/v1/orders":
            return self.send(404, {"error": "not found"})
        key = self.headers.get("Idempotency-Key")
        if key in STATE["keys"]:                   # 같은 키로 다시 오면 처음 답을 그대로
            return self.send(200, STATE["keys"][key])
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        STATE["orders"].append(body["book_id"])    # 올 때마다 주문이 하나 생긴다
        res = {"order_id": len(STATE["orders"])}
        if key:
            STATE["keys"][key] = res
        self.send(201, res)

    def log_message(self, *args):
        pass


def serve(port=PORT):
    reset()
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv
