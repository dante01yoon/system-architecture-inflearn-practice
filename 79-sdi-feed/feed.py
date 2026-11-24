"""뉴스 피드 fan-out 세 방식: push(쓸 때 퍼뜨림) · pull(읽을 때 모음) · hybrid(유명인만 pull)"""
import heapq
import random
from array import array

CELEB, KEEP = 10_000, 200   # 가정: 팔로워 1만 명 이상이면 유명인 · 타임라인 캐시는 사람마다 글 200개까지


def graph(n=100_000, k=10, seed=7):
    """사용자 0 = 유명인(나머지 모두가 팔로우), 1..n은 보통 사용자(각자 k명을 무작위로 팔로우)."""
    rnd = random.Random(seed)
    pick = lambda: [0] + rnd.sample(range(1, n + 1), k)
    following = [array("I")] + [array("I", pick()) for _ in range(n)]
    followers = [array("I") for _ in range(n + 1)]
    for u in range(1, n + 1):
        for v in following[u]:
            followers[v].append(u)
    return following, followers


class Feed:
    def __init__(self, following, followers, mode):
        self.following, self.followers, self.mode = following, followers, mode
        self.posts = {}       # 작성자 → [(시각, 글 id)]  (글 저장소)
        self.cache = {}       # 사용자 → [(시각, 글 id)]  (타임라인 캐시: id만)
        self.writes = self.reads = 0

    def pull_from(self, author):
        big = len(self.followers[author]) >= CELEB
        return self.mode == "pull" or (self.mode == "hybrid" and big)

    def post(self, author, t, pid):
        self.posts.setdefault(author, []).append((t, pid)); self.writes += 1
        if self.pull_from(author):
            return                                              # 퍼뜨리지 않는다
        for f in self.followers[author]:                        # fan-out on write
            tl = self.cache.setdefault(f, [])
            tl.append((t, pid)); self.writes += 1
            if len(tl) > KEEP:
                del tl[0]

    def timeline(self, user, n=10, cursor=None):
        """캐시 글과 pull 글을 시각 순으로 합친다(cursor = 마지막으로 본 시각)."""
        lists = []
        if self.mode != "pull":
            lists.append([(t, p, "push") for t, p in self.cache.get(user, [])])
            self.reads += 1
        for a in self.following[user]:
            if self.pull_from(a):                               # fan-out on read
                lists.append([(t, p, "pull") for t, p in self.posts.get(a, [])])
                self.reads += 1
        merged = heapq.merge(*(reversed(l) for l in lists), reverse=True)
        # shortcut: 같은 시각 글은 건너뛸 수 있다 · 실제로는 (시각, id)
        page = [x for x in merged if cursor is None or x[0] < cursor][:n]
        return page, (page[-1][0] if page else None)
