"""crypto-shredding 장난감: 손님마다 키 하나로 개인정보 칸을 암호화해 로그에 적고, 지울 때는 그 키만 버린다.
주의: toy_encrypt는 원리를 보여 주는 장난감이다(실제 서비스에 쓰지 않는다). 실제로는 AES-GCM 같은 검증된 라이브러리와 키 관리 서비스를 쓴다."""
import hashlib
import secrets


def _stream(key, nonce, n):
    out = b""
    for i in range(0, n, 32):
        out += hashlib.sha256(key + nonce + i.to_bytes(4, "big")).digest()
    return out[:n]


def toy_encrypt(key, text):
    nonce = secrets.token_bytes(12)
    data = text.encode()
    return nonce + bytes(a ^ b for a, b in zip(data, _stream(key, nonce, len(data))))


def toy_decrypt(key, blob):
    nonce, data = blob[:12], blob[12:]
    return bytes(a ^ b for a, b in zip(data, _stream(key, nonce, len(data)))).decode()


class KeyStore:
    def __init__(self):
        self.keys = {}

    def key(self, user):
        return self.keys.setdefault(user, secrets.token_bytes(32))

    def forget(self, user):
        self.keys.pop(user, None)      # 지우는 것은 키 하나뿐


def write_order(log, keys, user, book, price, day, name, address):
    k = keys.key(user)
    log.append({"user": user, "book": book, "price": price, "day": day,
                "name": toy_encrypt(k, name), "address": toy_encrypt(k, address)})


def read_personal(keys, event, field):
    k = keys.keys.get(event["user"])
    return toy_decrypt(k, event[field]) if k else None   # 키가 없으면 읽을 수 없다
