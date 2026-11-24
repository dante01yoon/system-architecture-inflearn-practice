"""연습 문제 풀이: 서버마다 카운터 범위를 미리 받아 쓰기(중앙 카운터는 범위를 줄 때만 부른다)
python3 solutions/key_range.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from idgen import encode  # noqa: E402


class Central:
    def __init__(self):
        self.next, self.calls = 1, 0

    def take(self, size):
        self.calls += 1
        lo = self.next
        self.next += size
        return lo, lo + size          # [lo, hi)


class Server:
    def __init__(self, central, size=1000):
        self.central, self.size, self.cur, self.hi = central, size, 0, 0

    def next_code(self):
        if self.cur >= self.hi:
            self.cur, self.hi = self.central.take(self.size)
        self.cur += 1
        return encode(self.cur - 1)


if __name__ == "__main__":
    central = Central()
    servers = [Server(central) for _ in range(3)]
    codes = [servers[i % 3].next_code() for i in range(10_000)]
    assert len(set(codes)) == len(codes)
    print(f"코드 {len(codes):,}개 · 겹침 0 · 중앙 카운터 호출 {central.calls}번")
    print("서버가 꺼지면 받아 둔 범위의 남은 번호는 버려진다(빈 번호가 생길 뿐 겹치지 않는다)")
