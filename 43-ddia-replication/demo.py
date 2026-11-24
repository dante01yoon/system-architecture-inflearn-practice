"""python3 demo.py 1 → 내가 쓴 글 읽기,  2 → 시간이 거꾸로 가는 읽기,  3 → 쿼럼 w + r > n"""
import sys

import quorum
from replica import Follower, Leader
from session import read_your_writes, sticky


def one():
    leader = Leader()
    f1 = Follower("f1", leader, lag=300, jitter=50, seed=7)
    seq = leader.write("review:DDIA", "minji ★★★★★", now=0)
    print("1) t=0ms  minji가 리뷰를 씀 → 리더에 저장 (로그 번호 1)")
    print(f"2) t=50ms 팔로워 f1에서 읽기 → {f1.read('review:DDIA', 50) or '(없음)'}   (f1은 로그 {f1.position(50)}번까지)")
    print("   방금 쓴 리뷰가 안 보임: read-your-writes 깨짐")
    where, got = read_your_writes(seq, leader, [f1], "review:DDIA", 50)
    print(f"3) 고침: 내가 쓴 번호 {seq}까지 따라온 곳에서만 읽기 → {where}: {got}")
    print(f"4) t=400ms f1도 따라옴 → f1: {f1.read('review:DDIA', 400)}")


def two():
    leader = Leader()
    fast = Follower("f1", leader, lag=100, seed=1)
    slow = Follower("f2", leader, lag=900, seed=2)
    leader.write("reviews:DDIA", 1, now=0)
    print("1) t=0ms  다른 손님이 리뷰를 씀 → 리뷰 1개")
    print(f"2) t=300ms minji의 첫 새로고침 → f1에서 리뷰 {fast.read('reviews:DDIA', 300)}개")
    print(f"3) t=400ms 두 번째 새로고침 → f2에서 리뷰 {slow.read('reviews:DDIA', 400) or 0}개")
    print("   있던 리뷰가 사라짐: monotonic reads 깨짐")
    f = sticky("minji", [fast, slow])
    reads = [f.read("reviews:DDIA", t) or 0 for t in (300, 400, 1000)]
    print(f"4) 고침: minji는 늘 {f.name}에서 읽기 → t=300·400·1000ms 리뷰 {reads}개")


def three():
    for w, r in ((2, 2), (1, 1)):
        reps = {name: (1, "재고 5권") for name in "ABC"}
        quorum.write(reps, "재고 4권", 2, to="AB"[:w])
        reads = quorum.all_reads(reps, r)
        stale = sum(v[0] < 2 for v in reads.values())
        print(f"{'1' if w == 2 else '2'}) n=3, w={w}, r={r} (w + r {'>' if w + r > 3 else '≤'} n): {''.join('AB'[:w])}에 버전 2를 씀")
        for frm, (ver, val) in reads.items():
            print(f"   {'+'.join(frm)}에서 읽기 → 버전 {ver} {val}")
        print(f"   옛 값을 읽은 경우 {stale}/{len(reads)}")


if __name__ == "__main__":
    {"1": one, "2": two, "3": three}[sys.argv[1] if len(sys.argv) > 1 else "1"]()
