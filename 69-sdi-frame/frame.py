"""답변 틀 일곱 걸음: 시간표(timeline)와 빈 연습지(worksheet)."""
STEPS = [  # (이름, 무게, 끝날 때 손에 있어야 하는 것)
    ("기능 요구", 3, "할 수 있어야 하는 일 셋"),
    ("비기능 요구", 3, "숫자 붙은 품질 셋"),
    ("어림셈", 3, "설계를 바꾸는 숫자만"),
    ("핵심 엔티티", 2, "저장할 것의 이름"),
    ("API", 5, "엔드포인트 두세 개"),
    ("큰 그림", 12, "요청 하나가 끝까지 가는 상자와 선"),
    ("깊게 파기", 12, "약한 곳 두세 군데와 대가"),
]
RESERVE = 5  # 처음 인사 2분 + 끝 질문 3분은 따로 둔다(가정)


def timeline(total, steps=STEPS, reserve=RESERVE):
    """[(이름, 시작 분, 끝 분)] — 남은 분을 무게 비율로 나눈다."""
    work = total - reserve
    if work < len(steps):
        raise ValueError(f"{total}분으로는 걸음마다 1분도 안 됩니다")
    wsum = sum(w for _, w, _ in steps)
    raw = [work * w / wsum for _, w, _ in steps]
    mins = [int(r) for r in raw]
    left = sorted(range(len(steps)), key=lambda i: (raw[i] - mins[i], i), reverse=True)
    for i in left[:work - sum(mins)]:  # 버린 소수점이 큰 걸음부터 1분씩(같으면 뒤 걸음)
        mins[i] += 1
    out, t = [("인사", 0, 2)], 2
    for (name, _, _), m in zip(steps, mins):
        out.append((name, t, t + m)); t += m
    return out + [("질문", t, total)]


def worksheet(problem, steps=STEPS):
    """문제 이름 하나로 연습지 마크다운을 만든다."""
    md = [f"# {problem} · 연습지", "", "가정은 말하고 확인받는다: 「~라고 가정할게요, 괜찮을까요?」", ""]
    for k, (name, _, done) in enumerate(steps, 1):
        md += [f"## {k}. {name}", f"끝나면 손에 있을 것: {done}", "- [ ] ", ""]
    return "\n".join(md)
