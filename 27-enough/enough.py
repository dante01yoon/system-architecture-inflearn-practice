"""위험 주도 설계 세 단계: 위험 매기기 → 기법 고르기 → 줄었는지 다시 보기."""
import csv
import unicodedata

TECHNIQUE = {"load": "부하 테스트", "unknown": "프로토타입", "structure": "다이어그램", "decision": "ADR"}
THRESHOLD = 6


def load(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            for k in ("likelihood", "impact", "after"):
                r[k] = int(r[k])
                if not 1 <= r[k] <= 5:
                    raise ValueError(f"{r['risk']}: {k}는 1~5")
            rows.append(r)
    return rows


def score(risk, likelihood=None):
    return (likelihood or risk["likelihood"]) * risk["impact"]


def prioritize(risks):
    return sorted(risks, key=score, reverse=True)


def plan(risks, threshold=THRESHOLD):
    """높은 순으로 (위험, 기법). 기준 아래는 그냥 만든다."""
    return [(r, TECHNIQUE[r["kind"]] if score(r) >= threshold else "그냥 만든다")
            for r in prioritize(risks)]


def evaluate(risks, threshold=THRESHOLD):
    """기법을 쓴 위험만 다시 매긴다: (위험, 전, 후, 아직 남았나)."""
    out = []
    for r in prioritize(risks):
        if score(r) >= threshold:
            after = score(r, r["after"])
            out.append((r, score(r), after, after >= threshold))
    return out


def pad(s, n):
    return s + " " * (n - sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s))
