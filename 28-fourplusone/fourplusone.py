"""4+1 뷰: 뷰마다 글자 그림을 찍고, 시나리오 한 줄로 네 뷰가 서로 맞는지 확인한다."""
VIEWS = {"logical": "논리 뷰", "process": "프로세스 뷰", "development": "개발 뷰", "physical": "물리 뷰"}
SEP = {"logical": " → ", "process": " → ", "development": " → ", "physical": ": "}


def show(model, view):
    return [f"{a}{SEP[view]}{', '.join(bs)}" if bs else a for a, bs in model[view].items()]


def walk(model, scenario):
    """단계마다 (번호, 이름, 문제들). 짚은 요소가 뷰에 있나, 프로세스가 서버에 올라갔나."""
    hosted = {p for ps in model["physical"].values() for p in ps}
    out = []
    for i, s in enumerate(scenario, 1):
        bad = []
        for v in ("logical", "process", "development"):
            if s[v] not in model[v]:
                bad.append(f"{s[v]}: {VIEWS[v]}에 없음")
        if s["process"] in model["process"] and s["process"] not in hosted:
            bad.append(f"{s['process']}: 어느 서버에도 없음")
        out.append((i, s["step"], bad))
    return out
