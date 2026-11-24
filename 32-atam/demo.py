"""서점 미니 ATAM: 유틸리티 트리 → 먼저 볼 시나리오 → 민감 지점과 트레이드오프 지점 → 위험 후보."""
import sys

from tree import DECISIONS, TREE, classify, ranked, risks


def main(part=""):
    # 녹화 터미널은 19줄 — 1은 1)·2), 2는 3)·4)(인자 없으면 전부)
    if part != "2":
        tree()
    if part != "1":
        decisions()


def tree():
    print("1) 유틸리티 트리 (중요도, 어려움)")
    last = None
    for q, sub, sid, text, imp, diff in TREE:
        if q != last:
            print(f"   {q}")
            last = q
        print(f"     └ {sub}: ({imp},{diff}) {sid} {text}")
    print("2) 먼저 볼 시나리오")
    for k, (_, _, sid, text, imp, diff) in enumerate(ranked(TREE)[:3], 1):
        print(f"   {k}. ({imp},{diff}) {sid} {text}")


def decisions():
    print("3) 설계 결정")
    for d, eff in DECISIONS.items():
        signs = " ".join(f"{q}{'+' if v > 0 else '-'}" for q, v in eff.items())
        print(f"   {classify(eff)}: {d} [{signs}]")
    print("4) 위험 후보: (H,H) 시나리오의 품질을 깎는 결정")
    for k, (d, sid, q) in enumerate(risks(TREE, DECISIONS), 1):
        print(f"   위험 {k}. {d} → {sid} {q}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
