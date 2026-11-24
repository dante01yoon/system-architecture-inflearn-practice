"""연습 풀이: DELETE /v1/wishlist/7을 더하고, 두 번 보내도 결과가 같은지(멱등) 확인한다."""
import json
import sys
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import api  # noqa: E402


class Handler(api.Handler):
    def do_DELETE(self):
        part = self.path.split("/")
        if part[1:3] != ["v1", "wishlist"] or not part[3].isdigit():
            return self.send(404, {"error": "not found"})
        api.STATE["wishlist"].discard(int(part[3]))   # 없어도 에러 없이 「없는 상태」로 만든다
        self.send(200, {"wishlist": sorted(api.STATE["wishlist"])})


api.reset()
srv = ThreadingHTTPServer(("127.0.0.1", 8922), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
for method in ("PUT", "DELETE", "DELETE"):
    with urlopen(Request("http://127.0.0.1:8922/v1/wishlist/7", method=method)) as r:
        print(method, r.status, json.loads(r.read())["wishlist"])
srv.shutdown()
