"""주도하는 어댑터 ②: HTTP JSON(POST /orders) → OrderService."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def serve(service, port=0):
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            try:
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                r = service.place_order(str(body["isbn"]), int(body["qty"]), str(body["card"]))
            except (KeyError, TypeError, ValueError):
                return self.reply(400, {"error": "isbn · qty · card가 필요합니다"})
            self.reply(200 if r.ok else 409, r.__dict__)

        def reply(self, status, data):
            raw = json.dumps(data, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def log_message(self, *args):  # 접속 기록은 화면에 찍지 않는다
            pass

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)
