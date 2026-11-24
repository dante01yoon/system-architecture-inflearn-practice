"""python3 demo.py 1 → push·pull·hybrid의 쓰기와 읽기 수,  2 → hybrid 타임라인 한 사람 합치기"""
import random
import sys

from feed import CELEB, Feed, graph


def workload(seed=3):
    rnd = random.Random(seed)
    posts = [(rnd.randrange(1, 100_001), rnd.uniform(0, 3600)) for _ in range(1_000)] + [(0, t) for t in (600.0, 1800.0, 3000.0)]
    loads = [rnd.randrange(1, 100_001) for _ in range(10_000)]
    return sorted(posts, key=lambda p: p[1]), loads


def compare():
    following, followers = graph()
    posts, loads = workload()
    print("1) 사용자 100,000명 · 유명인 1명(팔로워 100,000) · 보통은 10명 팔로우")
    print("   한 시간: 보통 글 1,000개 + 유명인 글 3개 · 타임라인 열기 10,000번")
    print("   방식     쓰기 합계   유명인 글 1개당   열기 1번 읽기")
    for mode in ("push", "pull", "hybrid"):
        f = Feed(following, followers, mode)
        for i, (a, t) in enumerate(posts):
            before = f.writes
            f.post(a, t, i)
            if a == 0:
                celeb = f.writes - before
        for u in loads:
            f.timeline(u)
        print(f"   {mode:<7} {f.writes:>10,}   {celeb:>15,}   {f.reads / len(loads):>12.1f}")
    print(f"2) hybrid = 팔로워 {CELEB:,}명 이상만 pull, 나머지는 push")


def merge():
    following, followers = graph()
    posts, _ = workload()
    f = Feed(following, followers, "hybrid")
    for i, (a, t) in enumerate(posts):
        f.post(a, t, i)
    user = max(range(1, 100_001), key=lambda u: len(f.cache.get(u, [])))   # push로 받은 글이 가장 많은 사람
    page, cur = f.timeline(user, n=4)
    print(f"1) 사용자 {user}의 첫 쪽 4개 (새 글부터)")
    for t, pid, src in page:
        print(f"   {int(t // 60):02d}분 {int(t % 60):02d}초  글 {pid:>4}  {src}")
    nxt, _ = f.timeline(user, n=3, cursor=cur)
    print(f"2) 다음 쪽은 cursor {int(cur // 60):02d}분 {int(cur % 60):02d}초보다 앞선 글부터: " + ", ".join(f"글 {p}" for _, p, _ in nxt))


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "1"
    {"1": compare, "2": merge}[arg]()
