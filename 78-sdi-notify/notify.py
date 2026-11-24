"""알림 시스템을 한 프로세스 안에서 작게: 채널별 큐 · 워커 재시도 · 중복 제거 · 사용자 설정 · DLQ"""
import random

MAX_TRY, BASE, CAP = 4, 1.0, 30.0   # 가정: 최대 4번, 1초에서 두 배씩, 30초 상한
PRIORITY = {"tx": 0, "mkt": 1}      # 거래 알림(인증번호·주문)이 마케팅보다 먼저
TEMPLATES = {"otp": "인증번호 {code}", "ship": "주문 {order} 배송 시작", "sale": "{title} 20% 할인"}


class Transient(Exception): pass    # 잠깐 실패 → 다시 해 볼 만함
class Permanent(Exception): pass    # 잘못된 번호 등 → 다시 해도 소용없음


class Provider:
    """APNs·FCM·SMS·메일 회사 대신 쓰는 가짜 제공자. seed로 실패가 매번 같다."""
    def __init__(self, fail, seed, bad=()):
        self.fail, self.rnd, self.bad, self.got = fail, random.Random(seed), set(bad), []

    def send(self, msg):
        if msg["to"] in self.bad:
            raise Permanent("bad address")
        if self.rnd.random() < self.fail:
            raise Transient("timeout")
        self.got.append(msg["id"])


class Service:
    def __init__(self, providers, prefs=None, limit=2, seed=1):
        self.providers, self.prefs, self.limit = providers, prefs or {}, limit
        self.queues = {ch: [] for ch in providers}   # 채널마다 큐 하나
        self.seen, self.sent_today, self.status, self.dlq = set(), {}, {}, []
        self.rnd, self.now, self.seq = random.Random(seed), 0.0, 0

    def submit(self, n):
        """API가 받는 곳: 중복 → 설정 → 횟수 제한 → 템플릿 → 큐."""
        if n["id"] in self.seen:
            return "dup"
        self.seen.add(n["id"])
        p = self.prefs.get(n["user"], {})
        ready = self.now
        if n["kind"] == "mkt":
            if n["channel"] in p.get("off", ()):
                return self._mark(n, "opt-out")
            hour = int(self.now // 3600) % 24
            q = p.get("quiet")
            if q and (hour >= q[0] or hour < q[1]):
                ready = (self.now // 86400) * 86400 + q[1] * 3600 + (86400 if hour >= q[0] else 0)
            day = (n["user"], int(ready // 86400))
            if self.sent_today.get(day, 0) >= self.limit:
                return self._mark(n, "rate-limit")
            self.sent_today[day] = self.sent_today.get(day, 0) + 1
        text = TEMPLATES[n["template"]].format(**n["data"])
        self._push(n["channel"], {**n, "text": text, "try": 0, "ready": ready})
        return self._mark(n, "queued" if ready == self.now else "held")

    def _mark(self, n, s):
        self.status[n["id"]] = s
        return s

    def _dead(self, msg, why):
        self._mark(msg, "dlq")
        self.dlq.append({**msg, "why": why})     # 사람이 나중에 보고 고치거나 다시 넣는다

    def _push(self, ch, msg):
        self.seq += 1
        self.queues[ch].append((PRIORITY[msg["kind"]], msg["ready"], self.seq, msg))

    def backoff(self, k):
        d = min(CAP, BASE * 2 ** (k - 1))
        return d / 2 + self.rnd.uniform(0, d / 2)      # 지수 백오프 + 지터

    def work(self, ch):
        """워커 하나: 준비된 것 중 우선순위가 높은 것부터 보내고, 실패하면 다시 넣는다."""
        q, retries = self.queues[ch], 0
        while q:
            ready = [e for e in q if e[1] <= self.now]
            if not ready:
                self.now = min(e[1] for e in q)            # 기다릴 게 없으면 시계를 넘긴다
                continue
            e = min(ready)
            q.remove(e)
            msg = e[3]
            msg["try"] += 1
            try:
                self.providers[ch].send(msg)
                self._mark(msg, "sent")
            except Permanent:
                self._dead(msg, "잘못된 주소")
            except Transient:
                if msg["try"] >= MAX_TRY:
                    self._dead(msg, f"{MAX_TRY}번 실패")
                else:
                    retries += 1
                    msg["ready"] = self.now + self.backoff(msg["try"])
                    self._push(ch, msg)
        return retries
