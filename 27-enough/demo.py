"""반짝 할인 전, 서점의 위험만큼만 설계하기."""
from enough import THRESHOLD, evaluate, load, pad, plan, score


def main():
    risks = load("risks.csv")
    print(f"1) 반짝 할인 전 위험 목록 risks.csv: {len(risks)}개")

    print(f"2) 점수(가능성 × 영향) 높은 순, {THRESHOLD}점 이상만 기법")
    rows = plan(risks)
    for r, technique in rows:
        print(f"   {score(r):>2}점  {pad(r['risk'], 18)}{r['likelihood']} × {r['impact']}  → {technique}")

    print("3) 기법을 쓴 뒤 다시 매기기")
    for r, before, after, left in evaluate(risks):
        print(f"   {pad(r['risk'], 18)}{before:>2} → {after:>2}  {'남음: 한 번 더' if left else '충분'}")

    done = sum(t != "그냥 만든다" for _, t in rows)
    print(f"4) 설계할 곳 {done}개, 바로 만들 곳 {len(rows) - done}개")


if __name__ == "__main__":
    main()
