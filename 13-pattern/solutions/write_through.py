"""연습 풀이: write-through. 값을 바꿀 때 원본과 캐시를 같은 자리에서 함께 바꾼다."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cache_aside  # noqa: E402
from demo import run  # noqa: E402


class Shop(cache_aside.Shop):
    def change_price(self, isbn, price):
        self.remote.set(isbn, price)
        self.cache[isbn] = price  # 지우지 않고 새 값으로 바로 채운다


if __name__ == "__main__":
    calls, stale = run(lambda r, c: Shop(r))
    assert (calls, stale) == (2, 0)
    print(f"write-through: 원격 호출 {calls}번 · 옛 가격 {stale}번")
