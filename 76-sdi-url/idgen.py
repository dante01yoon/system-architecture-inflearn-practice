"""고유 ID 만들기: base62와 Snowflake 비슷한 생성기 (표준 라이브러리만)"""
ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def encode(n):
    """정수 → base62 글자(0은 "0")."""
    s = ""
    while True:
        n, r = divmod(n, 62)
        s = ALPHABET[r] + s
        if n == 0:
            return s


def decode(s):
    n = 0
    for c in s:
        n = n * 62 + ALPHABET.index(c)
    return n


class ClockMovedBackwards(Exception):
    pass


EPOCH_MS = 1_767_225_600_000   # 2026-01-01 00:00 UTC, 이 서비스가 정한 시작 시각
TIME_BITS, MACHINE_BITS, SEQ_BITS = 41, 10, 12


class Snowflake:
    def __init__(self, machine, clock):
        assert 0 <= machine < 2 ** MACHINE_BITS
        self.machine, self.clock = machine, clock   # clock() = 지금 시각(밀리초)
        self.last, self.seq = -1, 0

    def next_id(self):
        now = self.clock()
        if now < self.last:
            raise ClockMovedBackwards(f"{self.last - now}ms 뒤로 감")
        if now == self.last:
            self.seq = (self.seq + 1) % 2 ** SEQ_BITS
            if self.seq == 0:            # 1ms에 4,096개를 다 씀 → 다음 1ms까지 기다림
                while now <= self.last:
                    now = self.clock()
        else:
            self.seq = 0
        self.last = now
        return (now - EPOCH_MS) << (MACHINE_BITS + SEQ_BITS) | self.machine << SEQ_BITS | self.seq


def parse(id_):
    """ID → (시작 뒤 밀리초, 기계 번호, 순번)."""
    return id_ >> (MACHINE_BITS + SEQ_BITS), id_ >> SEQ_BITS & (2 ** MACHINE_BITS - 1), id_ & (2 ** SEQ_BITS - 1)
