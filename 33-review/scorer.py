"""답을 읽어 위험 목록을 만든다: 심각도 = 영향 × 모자람, 높은 순."""
IMPACT = {"H": 3, "M": 2, "L": 1}
GAP = {"yes": 0, "partial": 1, "no": 2}
LEVEL = [(6, "높음"), (3, "중간"), (1, "낮음")]


def level(score):
    return next(name for floor, name in LEVEL if score >= floor)


def risks(checklist, answers):
    """[(심각도, 등급, id, 영역, 질문, 메모)] — yes는 빼고, 심각도 높은 순(같으면 체크리스트 순)."""
    out = []
    for qid, area, question, impact in checklist:
        answer, note = answers.get(qid, ("no", "답 없음"))
        score = IMPACT[impact] * GAP[answer]
        if score:
            out.append((score, level(score), qid, area, question, note))
    return sorted(out, key=lambda r: -r[0])
