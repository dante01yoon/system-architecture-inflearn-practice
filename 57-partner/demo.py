"""파트너 API 인증·인가 실행(장난감 코드): 1 = HMAC 서명 요청, 2 = 클라이언트 크레덴셜 토큰과 scope."""
import sys

from signing import Verifier, make_request
from tokens import Issuer, check

T0 = 1_763_100_000  # 고정 시계(초) — 실행마다 같은 결과
clock = [T0]
now = lambda: clock[0]  # noqa: E731


def signing():
    secret = b"partner-a-secret"
    api = Verifier({"k1": ("partner-a", secret)}, now)
    body = b'{"book": "DDIA", "qty": 1}'
    req = make_request("k1", secret, "POST", "/orders", body, T0, "n-001")
    print("1) partner-a가 주문 요청에 서명 (키 k1)")
    print("   서명할 글: POST · /orders · 시각 · nonce · 본문 해시")
    print("   → %d %s" % api.check(req))
    print("2) 가는 길에 누군가 본문을 바꿈: qty 1 → 100")
    bad = dict(req, body=b'{"book": "DDIA", "qty": 100}')
    print("   → %d %s" % api.check(bad))
    print("3) 엿본 요청을 그대로 한 번 더 보냄")
    print("   → %d %s" % api.check(req))
    print("4) 10분 전 시각으로 서명한 요청")
    old = make_request("k1", secret, "POST", "/orders", body, T0 - 600, "n-002")
    print("   → %d %s" % api.check(old))
    print("5) 다른 비밀값으로 서명한 요청")
    fake = make_request("k1", b"guess", "POST", "/orders", body, T0, "n-003")
    print("   → %d %s" % api.check(fake))


def tokens():
    key = b"issuer-signing-key"
    clients = {"partner-a": {"secrets": ["old-secret"], "scopes": {"orders:read"}}}
    auth = Issuer(key, clients, now)
    print("1) partner-a: grant_type=client_credentials, scope=orders:read")
    tok, _ = auth.token("partner-a", "old-secret", "orders:read")
    print("   → 토큰 발급 (aud bookshop-api, 10분 뒤 만료)")
    print("2) GET /orders (orders:read 필요) → %d %s" % check(key, tok, "orders:read", now))
    print("3) POST /orders (orders:write 필요) → %d %s" % check(key, tok, "orders:write", now))
    print("4) 받지 않은 scope를 달라고 하면 → %s" % auth.token("partner-a", "old-secret", "orders:write")[1])
    print("5) 토큰 끝 글자를 바꾸면 → %d %s" % check(key, tok[:-1] + ("1" if tok[-1] == "0" else "0"), "orders:read", now))
    other, _ = auth.token("partner-a", "old-secret", "orders:read", aud="stock-api")
    print("6) 재고 API용 토큰을 내밀면 → %d %s" % check(key, other, "orders:read", now))
    clock[0] = T0 + 660
    print("7) 11분 뒤 같은 토큰 → %d %s" % check(key, tok, "orders:read", now))
    print("8) 비밀값 교체: 옛 값과 새 값이 잠깐 함께 산다")
    clients["partner-a"]["secrets"].append("new-secret")
    for s in ["new-secret", "old-secret"]:
        print(f"   {s} → {'발급' if auth.token('partner-a', s, 'orders:read')[0] else '거절'}")
    clients["partner-a"]["secrets"].remove("old-secret")
    print(f"   옛 값 폐기 뒤 old-secret → {auth.token('partner-a', 'old-secret', 'orders:read')[1]}")


if __name__ == "__main__":
    {"1": signing, "2": tokens}[(sys.argv[1:] or ["1"])[0]]()
