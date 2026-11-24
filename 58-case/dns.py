"""AWS DynamoDB DNS 장애(2025-10-19~20)의 경쟁 상태를 작게: 계획기 → 적용기 둘 → 정리.
구조만 흉내 낸다. 세대 번호·주소·「두 세대 넘게 오래된 것 정리」는 설명용 가정이다."""


def plan(gen):
    return [f"10.0.{gen}.{i}" for i in (1, 2, 3)]       # 계획 = 로드 밸런서 주소 목록


class Zone:
    def __init__(self):
        self.plans = {1: plan(1)}                     # 세대 번호 → 계획
        self.applied, self.record = 1, plan(1)        # 지금 적용된 세대 · 손님이 받는 주소


class Enactor:
    def __init__(self, zone, safe=False):
        self.zone, self.safe = zone, safe

    def start(self, gen):
        self.gen = gen                                # 시작할 때 한 번만 비교한다
        return gen > self.zone.applied

    def finish(self):
        z = self.zone
        if z.applied not in z.plans:
            return "기준 계획이 없어 실패"              # 어긋난 상태: 다음 계획도 못 씀
        if self.safe and self.gen <= z.applied:
            return "거절"                              # 고친 뒤: 쓰는 순간 다시 비교
        z.applied, z.record = self.gen, plan(self.gen)
        return "적용"

    def cleanup(self, keep=2):
        z = self.zone
        for g in [g for g in z.plans if g < self.gen - keep]:
            if self.safe and g == z.applied:
                continue                              # 고친 뒤: 쓰고 있는 계획은 지우지 않음
            del z.plans[g]
            if g == z.applied:
                z.record = []                         # 쓰던 계획이 지워지면 주소도 사라진다
