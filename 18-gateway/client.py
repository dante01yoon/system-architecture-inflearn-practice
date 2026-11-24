"""모바일 앱 흉내: 요청마다 모바일 망 왕복 시간을 더하고, 몇 번 왕복했는지 센다."""
import json
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

MOBILE_RTT = 0.08  # 모바일 망 한 번 왕복을 0.08초로 흉내(같은 컴퓨터 안이라 실제 망은 거의 0초)


class App:
    def __init__(self, token=None):
        self.token, self.trips = token, 0

    def get(self, port, path):
        self.trips += 1
        time.sleep(MOBILE_RTT)
        req = Request(f"http://127.0.0.1:{port}{path}", headers={"Authorization": self.token or ""})
        try:
            with urlopen(req, timeout=2) as r:
                return r.status, json.load(r)
        except HTTPError as e:
            return e.code, json.load(e)
