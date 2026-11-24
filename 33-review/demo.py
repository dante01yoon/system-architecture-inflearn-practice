"""가벼운 리뷰: 체크리스트 → 서점 팀의 답 → 심각도 순 위험 목록 → 하나 고치고 다시."""
from collections import Counter

from answers import ANSWERS
from checklist import CHECKLIST
from scorer import risks


def show(answers):
    for score, lvl, qid, area, question, note in risks(CHECKLIST, answers):
        print(f"   [{lvl}] {score} {qid} {area} · {note}")


def main():
    print("1) 체크리스트", len(CHECKLIST), "문항:", " ".join(dict.fromkeys(a for _, a, _, _ in CHECKLIST)))
    got = Counter(ANSWERS.get(q, ("no",))[0] for q, *_ in CHECKLIST)
    print(f"2) 서점 팀의 답  yes {got['yes']} · partial {got['partial']} · no {got['no']} (R1 답 없음 → no)")
    print("3) 위험 목록 (심각도 = 영향 × 모자람)")
    show(ANSWERS)
    print("4) 결제가 멈추면 '결제 대기'로 접수하게 고친 뒤")
    fixed = dict(ANSWERS, F1=("yes", "결제 대기 큐"))
    before, after = risks(CHECKLIST, ANSWERS), risks(CHECKLIST, fixed)
    high = lambda r: sum(x[1] == "높음" for x in r)
    print(f"   위험 {len(before)}개 -> {len(after)}개, 높음 {high(before)} -> {high(after)}")
    print(f"   이제 맨 위: {after[0][2]} {after[0][3]} · {after[0][5]}")


if __name__ == "__main__":
    main()
