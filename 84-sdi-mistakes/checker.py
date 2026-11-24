"""연습 답변 대본(시각이 붙은 텍스트)에서 면접 실수 신호를 센다. 공식 채점표가 아니라 연습용 거울이다."""
import re

LINE = re.compile(r"\[(\d\d):(\d\d)\] (#|나:|면접관:) ?(.*)")
NUMBER = re.compile(r"\d[\d,.]*\s*(만|억|명|번|초|ms|밀리초|GB|TB|MB|QPS|%|퍼센트|권|배)")
TRADE = ("대신", "비용", "트레이드오프", "대가")
FAIL = ("죽으면", "장애", "실패", "복제", "재시도", "다운")


def parse(text):
    """줄마다 (분, 누가, 말). '#'은 걸음 시작 표시다."""
    rows = []
    for raw in text.splitlines():
        m = LINE.match(raw.strip())
        if m:
            rows.append((int(m[1]) + int(m[2]) / 60, m[3].rstrip(":"), m[4]))
    return rows


def phases(rows, end):
    """걸음 이름 → 쓴 분. 다음 '#'(또는 끝)까지가 그 걸음의 시간이다."""
    marks = [(t, say) for t, who, say in rows if who == "#"] + [(end, None)]
    return {name: round(b - a) for (a, name), (b, _) in zip(marks, marks[1:])}


def check(text, end=45):
    rows = parse(text)
    mine = [(t, say) for t, who, say in rows if who == "나"]
    req_end = next((t for t, who, say in rows if who == "#" and say != "요구"), end)
    gaps = [b[0] - a[0] for a, b in zip(mine, mine[1:])]
    return {
        "phases": phases(rows, end),
        "요구 질문": sum(1 for t, say in mine if t < req_end and say.endswith("?")),
        "숫자": sum(len(NUMBER.findall(say)) for _, say in mine),
        "트레이드오프": sum(say.count(w) for _, say in mine for w in TRADE),
        "장애 대비": sum(1 for _, say in mine if any(w in say for w in FAIL)),
        "말 없는 틈": round(max(gaps, default=0)),
    }


RULES = [  # (신호, 통과 조건, 고칠 것)
    ("요구 질문", lambda v: v >= 3, "그리기 전에 묻기 · 세 개 이상"),
    ("숫자", lambda v: v >= 3, "사용자 수 · 초당 요청 · 용량을 숫자로"),
    ("트레이드오프", lambda v: v >= 2, "고른 것마다 「대신」 · 「비용」 한 문장"),
    ("장애 대비", lambda v: v >= 1, "「이게 죽으면?」을 스스로 묻기"),
    ("말 없는 틈", lambda v: v <= 3, "3분 넘게 조용하면 생각을 소리 내기"),
]


def flags(result):
    """통과 못 한 신호의 고칠 것 목록. 깊게 파기가 10분 미만이어도 하나 더한다."""
    out = [fix for name, ok, fix in RULES if not ok(result[name])]
    if result["phases"].get("깊게 파기", 0) < 10:
        out.append("깊게 파기 10분 이상 · 큰 그림을 시계로 끊기")
    return out
