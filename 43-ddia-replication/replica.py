"""리더 하나 + 비동기 팔로워. 시간은 밀리초 숫자로 흉내 낸다(seed 고정이라 실행마다 같다)."""
import random


class Leader:
    def __init__(self):
        self.log = []                               # 복제 로그: (번호, 쓴 시각, 키, 값)

    def write(self, key, value, now):
        self.log.append((len(self.log) + 1, now, key, value))
        return len(self.log)                        # 이 쓰기의 로그 번호

    def read(self, key, now):
        return _state(self.log).get(key)


class Follower:
    def __init__(self, name, leader, lag, jitter=0, seed=1):
        self.name, self.leader, self.lag = name, leader, lag
        self.rng, self.arrive = random.Random(seed), {}
        self.jitter = jitter

    def position(self, now):
        """now까지 도착해 적용한 마지막 로그 번호(비동기라 리더보다 늦다)."""
        pos = 0
        for seq, t, _, _ in self.leader.log:
            if seq not in self.arrive:
                self.arrive[seq] = t + self.lag + self.rng.randint(0, self.jitter)
            if self.arrive[seq] > now:
                break
            pos = seq
        return pos

    def read(self, key, now):
        return _state(self.leader.log[:self.position(now)]).get(key)


def _state(entries):
    state = {}
    for _, _, key, value in entries:
        state[key] = value
    return state
