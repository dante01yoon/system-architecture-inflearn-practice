"""연습 풀이: 팔로우를 끊으면 push로 이미 넣어 둔 그 사람 글이 캐시에 남는다 → 끊을 때 캐시에서 걸러 낸다."""
import sys
from array import array
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from feed import Feed  # noqa: E402


def unfollow(f, user, author):
    f.following[user] = array("I", [a for a in f.following[user] if a != author])
    f.followers[author] = array("I", [u for u in f.followers[author] if u != user])
    mine = {p for _, p in f.posts.get(author, [])}
    f.cache[user] = [x for x in f.cache.get(user, []) if x[1] not in mine]


following = [array("I"), array("I"), array("I", [1])]
followers = [array("I"), array("I", [2]), array("I")]
f = Feed(following, followers, "push")
f.post(1, 1.0, 100)
print("끊기 전:", [p for _, p, _ in f.timeline(2)[0]])
unfollow(f, 2, 1)
print("끊은 뒤:", [p for _, p, _ in f.timeline(2)[0]])
