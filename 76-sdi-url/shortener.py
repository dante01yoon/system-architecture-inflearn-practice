"""메모리 안 URL 단축기: 카운터 + base62, 직접 고른 이름, 만료"""
import hashlib

from idgen import encode


def hash_code(url, k=7):
    """해시 방식: URL의 SHA-256 앞부분을 base62 k글자로 자른다(다른 URL도 겹칠 수 있다)."""
    n = int.from_bytes(hashlib.sha256(url.encode()).digest()[:8], "big")
    return encode(n % 62 ** k).rjust(k, "0")


class Shortener:
    def __init__(self, clock, start=0):
        self.clock, self.counter = clock, start   # clock() = 지금 시각(초)
        self.rows = {}                            # code → (긴 URL, 만료 시각 또는 None)

    def create(self, url, alias=None, ttl=None):
        if alias:
            if alias in self.rows:
                raise ValueError(f"이미 쓰는 이름: {alias}")
            code = alias
        else:
            code = None
            while code is None or code in self.rows:   # 이름으로 먼저 쓴 글자는 건너뜀
                self.counter += 1
                code = encode(self.counter)
        self.rows[code] = (url, self.clock() + ttl if ttl else None)
        return code

    def redirect(self, code):
        """GET /{code} → (상태 코드, Location)."""
        if code not in self.rows:
            return 404, None
        url, expires = self.rows[code]
        if expires is not None and self.clock() >= expires:
            return 410, None
        return 302, url
