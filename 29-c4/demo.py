"""C4 모델 검사기. 인자 없이: 엉망인 모델과 고친 모델 검사. 1·2·3: 그 레벨 다이어그램을 목록으로."""
import sys

from bookshop import bookshop
from c4 import lint, outline


def check(title, model):
    problems = lint(model)
    print(f"{title}: 문제 {len(problems)}개")
    for p in problems:
        print(f"   - {p}")


def main(args):
    if not args:
        check("1) 엉망인 모델 검사", bookshop(messy=True))
        check("2) 고친 모델 검사", bookshop())
        return
    level = int(args[0])
    model = bookshop()
    d = model.diagrams[level - 1]
    print(f"레벨 {level} · {d.title}")
    for line in outline(model, d):
        print("   " + line)


if __name__ == "__main__":
    main(sys.argv[1:])
