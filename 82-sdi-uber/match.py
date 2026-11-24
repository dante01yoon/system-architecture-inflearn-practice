"""배차: 기사 한 명을 원자적으로 잡기(조건부 갱신 + 리스) · 수락 시간 초과"""
import threading
import time

ACCEPT = 10    # 기사가 수락할 시간(초, 가정) = 잡은 표시의 리스


class Store:
    """기사 상태 저장소. claim은 「비어 있을 때만 쓴다」를 한 번에 한다.
    실제로는 Redis SET NX PX · DB 조건부 UPDATE가 이 자리에 온다."""

    def __init__(self):
        self.who, self._lock = {}, threading.Lock()

    def claim(self, d, ride, now):
        with self._lock:                                   # 확인과 쓰기 사이에 아무도 끼지 못한다
            cur = self.who.get(d)
            if cur and cur[1] > now:                       # 리스가 살아 있으면 남의 것
                return False
            self.who[d] = (ride, now + ACCEPT)
            return True

    def claim_naive(self, d, ride, now):
        """나쁜 예: 확인하고, 잠깐 뒤에 쓴다 — 그 틈에 다른 요청이 끼어든다."""
        cur = self.who.get(d)
        if cur and cur[1] > now:
            return False
        time.sleep(0.05)                                   # 네트워크 왕복 흉내
        self.who[d] = (ride, now + ACCEPT)
        return True


def dispatch(store, ride, cands, now, naive=False):
    """가까운 순 후보 중 처음으로 잡힌 기사를 돌려준다."""
    grab = store.claim_naive if naive else store.claim
    for _, d in cands:
        if grab(d, ride, now):
            return d
    return None


def race(store, rides, cands, now, naive=False):
    """두 요청을 동시에 출발시킨다."""
    got, go = {}, threading.Barrier(len(rides))

    def run(r):
        go.wait()
        got[r] = dispatch(store, r, cands, now, naive)

    ts = [threading.Thread(target=run, args=(r,)) for r in rides]
    [t.start() for t in ts]
    [t.join() for t in ts]
    return got
