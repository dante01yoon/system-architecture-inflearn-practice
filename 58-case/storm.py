"""복구 뒤 리스 몰림(AWS 보고서의 DWFM 혼잡 붕괴)을 작게. 서버 수·처리량·타임아웃은 설명용 가정이다."""
from collections import deque


def lease_storm(hosts=600, per_tick=50, timeout=4, ticks=60, limit=None):
    queue, sent, leased, wasted, log = deque(), {}, set(), 0, {}
    for t in range(ticks + 1):
        for h in range(hosts):                        # 1) 서버들
            if h in leased or (h in sent and t - sent[h] <= timeout):
                continue                              # 이미 받았거나 아직 기다리는 중
            if limit is not None and len(queue) >= limit:
                sent.pop(h, None)                     # 고친 뒤: 줄이 길면 받지 않음 → 다음 틱에
                continue
            queue.append((h, t)); sent[h] = t
        for _ in range(min(per_tick, len(queue))):    # 2) 관리자
            h, t0 = queue.popleft()
            if h in leased or t - t0 > timeout:
                wasted += 1                           # 보낸 쪽은 이미 포기했다 → 헛일
            else:
                leased.add(h)
        log[t] = (len(leased), len(queue), wasted)
    return log
