"""연습 면접 뒤 스스로 채점하는 점검표: 네 영역 × 세 문항(예/아니요)."""
RUBRIC = [
    ("문제 탐색", [
        ("모호한 곳을 질문으로 줄였다", "상자를 그리기 전에 누가, 얼마나, 무엇을 묻기"),
        ("가장 중요한 문제를 골랐다", "기능을 셋으로 줄이고 나머지는 뺀다고 말하기"),
        ("요구를 숫자로 적었다", "지연·규모·가용성을 숫자 하나씩으로 적기"),
    ]),
    ("해법 설계", [
        ("동작하는 큰 그림을 끝까지 그렸다", "요청 하나가 들어와 나갈 때까지 선을 잇기"),
        ("API와 데이터 모양을 정했다", "엔드포인트 두세 개와 표 두세 개부터 적기"),
        ("요구마다 맡는 부분을 짚었다", "요구 목록을 다시 읽으며 그림에서 손가락으로 짚기"),
    ]),
    ("기술 깊이", [
        ("필요한 곳에서 세부까지 내려갔다", "가장 약한 곳 하나를 골라 5분 깊게 파기"),
        ("트레이드오프를 말했다", "「A 대신 B, 이유는 C, 대가는 D」로 말하기"),
        ("장애 지점과 대비를 말했다", "「이게 죽으면?」을 상자마다 한 번씩 묻기"),
    ]),
    ("기술 소통", [
        ("생각을 소리 내어 설명했다", "조용히 그리지 말고 지금 하는 일을 한 문장씩 말하기"),
        ("가정을 말하고 확인받았다", "「~라고 가정할게요, 괜찮을까요?」라고 묻기"),
        ("면접관의 힌트를 반영했다", "질문을 받으면 방어하지 말고 그 방향으로 고쳐 보기"),
    ]),
]
ITEMS = sum(len(qs) for _, qs in RUBRIC)


def parse(text):
    """「y n y …」(예=y, 아니요=n) 12개를 True/False 목록으로. 공백·쉼표는 무시."""
    marks = [c for c in text.lower() if c in "yn"]
    if len(marks) != ITEMS:
        raise ValueError(f"답이 {len(marks)}개 — {ITEMS}개(y 또는 n)가 필요합니다")
    return [c == "y" for c in marks]


def score(answers):  # 영역마다 (이름, 점수, 만점, 고칠 점 하나 또는 None)
    out, k = [], 0
    for name, qs in RUBRIC:
        got = answers[k:k + len(qs)]
        miss = [tip for (q, tip), ok in zip(qs, got) if not ok]
        out.append((name, sum(got), len(qs), miss[0] if miss else None))
        k += len(qs)
    return out


def weakest(rows):
    """점수 비율이 가장 낮은 영역(같으면 앞쪽)."""
    return min(rows, key=lambda r: r[1] / r[2])[0]
