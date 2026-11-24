"""서점 arc42 문서를 검사한다: 뼈대 → 반쯤 채운 문서 → 9장의 ADR 링크."""
import sys
from pathlib import Path

from arc42 import SECTIONS, check, skeleton

HERE = Path(__file__).parent


def main(part=""):
    # 녹화 터미널은 19줄 — 1은 1)·2), 2는 3)만(인자 없으면 전부)
    report, links = check(HERE / "bookshop/arc42.md")
    if part != "2":
        sections(report)
    if part != "1":
        adr_links(links)


def sections(report):
    out = HERE / "skeleton.md"
    out.write_text(skeleton("온라인 서점"), encoding="utf-8")
    print(f"1) 뼈대 만들기: {out.name} · {len(SECTIONS)}장")
    print("2) bookshop/arc42.md 검사")
    for n, name, st in report:
        print(f"   {st}  {n:2}. {name}")
    count = {s: sum(1 for *_, st in report if st == s) for s in ("채움", "짧음", "빈칸")}
    print("   " + " · ".join(f"{s} {c}" for s, c in count.items()))


def adr_links(links):
    print("3) 9장의 결정 링크")
    for adr, st in links:
        print(f"   {adr:<33} {st}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
