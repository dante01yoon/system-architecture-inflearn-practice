"""서버를 스레드로 띄우고 내리기, 요청 하나 보내기."""
import json
import threading
from urllib.error import HTTPError
from urllib.request import urlopen


def start(server):
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def stop(server):
    server.shutdown()
    server.server_close()


def get(url):
    try:
        with urlopen(url, timeout=2) as r:
            return json.load(r)
    except HTTPError as e:
        return json.load(e)
    except OSError:
        return {"error": "연결 안 됨"}
