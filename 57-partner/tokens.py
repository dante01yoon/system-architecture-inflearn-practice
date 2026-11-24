"""클라이언트 크레덴셜 토큰 발급과 검사 — 장난감입니다. 진짜 JWT가 아니고,
실서비스는 검증된 인가 서버와 JWT 라이브러리를 쓰세요."""
import base64
import hashlib
import hmac
import json


def _mac(key, body):
    return hmac.new(key, body.encode(), hashlib.sha256).hexdigest()


class Issuer:
    def __init__(self, key, clients, now, ttl=600):
        self.key, self.clients, self.now, self.ttl = key, clients, now, ttl

    def token(self, client_id, secret, scope, aud="bookshop-api"):
        c = self.clients.get(client_id)
        if not c or not any(hmac.compare_digest(s, secret)
                            for s in c["secrets"]):
            return None, "invalid_client"
        asked = set(scope.split())
        if not asked <= c["scopes"]:
            return None, "invalid_scope"
        claims = {"sub": client_id, "scope": " ".join(sorted(asked)),
                  "aud": aud, "exp": self.now() + self.ttl}
        body = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode()
        return body + "." + _mac(self.key, body), None


def check(key, token, need, now, aud="bookshop-api"):
    body, _, mac = token.partition(".")
    if not hmac.compare_digest(_mac(key, body), mac):  # 알고리즘은 서버가 정한다
        return 401, "서명 불일치"
    claims = json.loads(base64.urlsafe_b64decode(body))
    if claims["aud"] != aud:
        return 401, "다른 서비스용 토큰"
    if claims["exp"] <= now():
        return 401, "만료"
    if need not in claims["scope"].split():
        return 403, f"{need} 권한 없음"
    return 200, claims["sub"]
