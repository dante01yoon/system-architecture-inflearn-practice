"""실시간 베스트셀러: 1분 칸 60개 창 · 책 번호로 나눈 샤드 · 샤드별 상위 k를 힙으로 합치기 · 핫 책은 나눠 쓰기."""
import hashlib
import heapq
from collections import Counter
from itertools import chain
from operator import itemgetter


class Window:
    """최근 minutes분만 센다. 칸 하나 = 1분."""
    def __init__(self, minutes=60):
        self.minutes, self.buckets = minutes, {}

    def add(self, t, book):
        self.buckets.setdefault(int(t // 60), Counter())[book] += 1

    def counts(self, now):
        end = int(now // 60)
        for m in [m for m in self.buckets if m < end - self.minutes]:
            del self.buckets[m]                      # 창 밖으로 밀려난 칸은 버린다
        return sum((c for m, c in self.buckets.items() if m < end), Counter())


def shard_of(book, n):
    return int(hashlib.md5(book.encode()).hexdigest(), 16) % n


class Leaderboard:
    def __init__(self, shards=4, hot=()):
        self.shards = [Window() for _ in range(shards)]
        self.writes, self.hot, self.turn = [0] * shards, set(hot), 0

    def add(self, t, book):
        if book in self.hot:                         # 핫 책은 샤드를 돌아가며 쓴다
            s, self.turn = self.turn % len(self.shards), self.turn + 1
        else:
            s = shard_of(book, len(self.shards))     # 나머지 책은 늘 같은 샤드
        self.shards[s].add(t, book)
        self.writes[s] += 1

    def top(self, k, now):
        counts = [w.counts(now) for w in self.shards]
        hot = Counter({b: sum(c.pop(b, 0) for c in counts) for b in self.hot})  # 나눠 쓴 책은 합친다
        local = [heapq.nlargest(k, c.items(), key=itemgetter(1)) for c in counts]
        return heapq.nlargest(k, chain(hot.items(), *local), key=itemgetter(1))


def exact_top(events, k, now, minutes=60):
    end = int(now // 60) * 60
    return Counter(b for t, b in events if end - minutes * 60 <= t < end).most_common(k)
