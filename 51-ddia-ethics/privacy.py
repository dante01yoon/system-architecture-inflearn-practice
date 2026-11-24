"""데이터 최소화 + 가명 처리. 목적(판매 통계)에 필요한 칸만 남기고, 손님 아이디는 비밀 키로 만든 가명으로 바꾼다."""
import hashlib
import hmac

SECRET = b"demo-secret-change-me"   # 예제용 키. 실제로는 코드 밖(키 관리 서비스)에 둔다

PURPOSE = {"판매 통계": ["user", "book", "price", "day"]}   # 목적마다 필요한 칸


def pseudonym(user_id, secret=SECRET):
    """같은 손님 → 같은 가명. 키 없이는 가명에서 아이디를 되찾을 수 없다."""
    return hmac.new(secret, user_id.encode(), hashlib.sha256).hexdigest()[:10]


def minimize(raw, purpose, secret=SECRET):
    event = {"user": pseudonym(raw["user_id"], secret)}           # 아이디 대신 가명
    event.update({k: raw[k] for k in PURPOSE[purpose] if k in raw})  # 목록에 없는 칸은 버린다
    return event
