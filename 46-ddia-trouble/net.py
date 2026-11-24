"""믿을 수 없는 네트워크. 손님(클라이언트)은 타임아웃만 본다 — 요청이 사라졌는지, 응답이 사라졌는지, 늦는지 모른다."""
import random

TIMEOUT = 1000                                   # 밀리초. 손님이 기다리는 한도(추측값)


class PaymentServer:
    def __init__(self):
        self.charges, self.seen = [], {}         # 결제 기록, 멱등성 키 → 결과

    def charge(self, amount, key=None):
        if key in self.seen:
            return self.seen[key]                # 같은 키는 다시 결제하지 않는다
        self.charges.append(amount)
        result = f"결제 {len(self.charges)}건째"
        if key:
            self.seen[key] = result
        return result


def call(server, amount, fate, key=None, seed=1):
    """fate = 무슨 일이 일어날지. 손님이 본 것과 걸린 시간만 돌려준다."""
    delay = random.Random(seed).randint(1500, 2500) if fate == "slow" else 80
    if fate == "lost_request":
        return "타임아웃", TIMEOUT               # 서버는 요청을 받지도 못함
    answer = server.charge(amount, key)          # 서버는 일을 함
    if fate == "lost_response" or delay > TIMEOUT:
        return "타임아웃", TIMEOUT               # 답이 안 오거나 너무 늦음
    return answer, delay
