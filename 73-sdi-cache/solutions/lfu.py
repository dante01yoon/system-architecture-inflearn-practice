"""연습 풀이: 가장 적게 쓴 것부터 내보내는 LFU를 만들고 LRU와 적중률을 비교한다. 실행: python3 solutions/lfu.py"""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cache import LRU, zipf_keys


class LFU:
    def __init__(self, size):
        self.size, self.data, self.freq = size, {}, Counter()
        self.hits = self.misses = 0

    def get(self, key):
        if key in self.data:
            self.freq[key] += 1
            self.hits += 1
            return self.data[key]
        self.misses += 1
        return None

    def put(self, key, value):
        if key not in self.data and len(self.data) >= self.size:
            victim = min(self.data, key=lambda k: self.freq[k])   # shortcut: O(n) 고르기, 크면 빈도별 묶음 목록으로
            del self.data[victim]
            del self.freq[victim]
        self.data[key] = value
        self.freq[key] += 1

    def ratio(self):
        return self.hits / max(1, self.hits + self.misses)


if __name__ == "__main__":
    reqs = zipf_keys(10_000, 100_000)
    for size in (10, 100, 1_000):
        out = []
        for cls in (LRU, LFU):
            c = cls(size)
            for k in reqs:
                if c.get(k) is None:
                    c.put(k, k)
            out.append(f"{cls.__name__} {c.ratio():.1%}")
        print(f"크기 {size:>5,}: " + " · ".join(out))
