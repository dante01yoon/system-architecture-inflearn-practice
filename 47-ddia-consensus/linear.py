"""작은 선형성 검사기: 레지스터(값 하나) 기록에서, 실제 시간 순서를 지키면서 값이 맞는 한 줄 순서가 있는지 모두 찾아본다."""
from itertools import permutations


def op(who, kind, value, start, end):
    return {"who": who, "kind": kind, "value": value, "start": start, "end": end}


def check(history, initial):
    """선형화할 수 있으면 그 순서(이름 목록), 없으면 None. 기록이 작을 때만(모든 순서를 다 본다)."""
    for order in permutations(history):
        # 실제 시간: a가 끝난 뒤 b가 시작했으면 a가 먼저여야 한다
        if any(b["end"] < a["start"] for i, a in enumerate(order) for b in order[i + 1:]):
            continue
        value, ok = initial, True
        for o in order:                          # 한 줄로 세웠을 때 읽기는 바로 앞 쓰기의 값을 봐야 한다
            if o["kind"] == "write":
                value = o["value"]
            elif o["value"] != value:
                ok = False
                break
        if ok:
            return [f'{o["who"]} {"쓰기" if o["kind"] == "write" else "읽기"}' for o in order]
    return None
