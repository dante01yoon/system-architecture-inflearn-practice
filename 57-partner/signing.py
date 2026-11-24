"""파트너 요청 HMAC 서명과 검증 — 강의용 장난감입니다. 실서비스에 그대로 쓰지 마세요."""
import hashlib
import hmac

WINDOW = 300  # 초: 시각이 이만큼 넘게 벌어진 요청은 거절


def string_to_sign(method, path, ts, nonce, body):
    body_hash = hashlib.sha256(body).hexdigest()
    return "\n".join([method, path, str(ts), nonce, body_hash])


def sign(secret, method, path, ts, nonce, body):
    msg = string_to_sign(method, path, ts, nonce, body).encode()
    return hmac.new(secret, msg, hashlib.sha256).hexdigest()


class Verifier:
    def __init__(self, keys, now):
        self.keys = keys  # 키 id → (파트너, 비밀값). 교체 중엔 둘이 함께 산다
        self.now = now
        self.seen = {}    # 이미 쓴 nonce → 시각

    def check(self, req):
        key = self.keys.get(req["key_id"])
        if key is None:
            return 401, "모르는 키"
        if abs(self.now() - req["ts"]) > WINDOW:
            return 401, "시각이 5분 밖"
        partner, secret = key
        expect = sign(secret, req["method"], req["path"], req["ts"],
                      req["nonce"], req["body"])
        if not hmac.compare_digest(expect, req["sig"]):
            return 401, "서명 불일치"
        # 서명을 통과한 요청만 nonce를 기록한다(아무나 캐시를 채우지 못하게)
        self.seen = {n: t for n, t in self.seen.items()
                     if self.now() - t <= WINDOW}
        if req["nonce"] in self.seen:
            return 401, "이미 쓴 nonce (재전송)"
        self.seen[req["nonce"]] = req["ts"]
        return 200, partner


def make_request(key_id, secret, method, path, body, ts, nonce):
    sig = sign(secret, method, path, ts, nonce, body)
    return {"key_id": key_id, "method": method, "path": path,
            "body": body, "ts": ts, "nonce": nonce, "sig": sig}
