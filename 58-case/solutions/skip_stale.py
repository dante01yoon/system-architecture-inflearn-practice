"""연습 풀이: 보낸 쪽이 이미 포기한 요청은 처리하지 않고 버리면(버리는 비용 0으로 가정) 조절 없이도 붕괴가 풀릴까?
python3 solutions/skip_stale.py"""
from collections import deque


def lease_storm_skip(hosts=600, per_tick=50, timeout=4, ticks=60):
    queue, sent, leased = deque(), {}, set()
    for t in range(ticks + 1):
        for h in range(hosts):
            if h in leased or (h in sent and t - sent[h] <= timeout):
                continue
            queue.append((h, t)); sent[h] = t
        done = 0
        while queue and done < per_tick:
            h, t0 = queue.popleft()
            if h in leased or t - t0 > timeout:
                continue                              # 기한이 지난 요청은 그냥 버린다(일로 치지 않음)
            leased.add(h); done += 1
        if len(leased) == hosts:
            return t
    return None


t = lease_storm_skip()
print(f"기한 지난 요청 버리기 → {t}틱에 600대 모두 리스")
assert t is not None
