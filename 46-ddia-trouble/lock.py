"""잠금 리스와 펜싱 토큰(Kleppmann, 「How to do distributed locking」, 2016-02-08의 예를 서점 재고로)."""


class LockService:
    def __init__(self, lease=10):
        self.lease, self.holder, self.until, self.token = lease, None, -1, 32

    def acquire(self, who, now):
        if self.holder and now < self.until:
            return None                          # 아직 다른 사람 것
        self.token += 1                          # 잠금을 줄 때마다 1씩 커지는 번호
        self.holder, self.until = who, now + self.lease
        return self.token


class Storage:
    def __init__(self, fencing):
        self.fencing, self.value, self.max_token = fencing, "재고 5권", 0

    def write(self, value, token):
        if self.fencing and token < self.max_token:
            return False                         # 더 큰 번호를 이미 봤다 → 옛 잠금
        self.max_token = max(self.max_token, token)
        self.value = value
        return True
