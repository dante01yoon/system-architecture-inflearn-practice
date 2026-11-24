"""레거시 서점을 문(facade) 뒤에서 조금씩 갈아 끼운다: catalog → reviews. 손님은 늘 같은 문만 부른다."""
import contextlib
import io
import sys

from facade import Facade
import legacy

ISBNS = list(legacy.BOOKS)
CA = ISBNS[0]


def ask(f, name, isbn=CA, *args):
    who, body = f.handle(name, isbn, *args)
    print(f"   {name:<8} -> {who:<6} {body}")


def parallel(f, name):
    f.routes[name] = "compare"
    for isbn in ISBNS:
        f.handle(name, isbn)
    same = sum(ok for n, _, ok in f.compared if n == name)
    print(f"   {name} 책 {len(ISBNS)}권 나란히: 같음 {same}, 다름 {len(ISBNS) - same}")


def main(part=""):
    f = Facade({"catalog": "legacy", "reviews": "legacy", "order": "legacy"})
    # 녹화 터미널은 19줄 — 1은 1)~3), 2는 4)~6)(인자 없으면 전부). 2도 1)~3)을 조용히 돌려 같은 안내표에서 시작
    with contextlib.redirect_stdout(io.StringIO()) if part == "2" else contextlib.nullcontext():
        first(f)
    if part != "1":
        rest(f)


def first(f):
    print("1) 처음: 문은 있지만 모든 요청이 레거시로")
    ask(f, "catalog"), ask(f, "reviews"), ask(f, "order", CA, 1)

    print("2) catalog 나란히 돌리기: 레거시가 답하고, 새 서비스 답과 비교만")
    parallel(f, "catalog")

    print("3) catalog를 새 서비스로: 길 안내표 한 줄")
    f.routes["catalog"] = "new"
    ask(f, "catalog"), ask(f, "reviews")


def rest(f):
    print("4) reviews도 나란히 돌린 뒤 새 서비스로")
    parallel(f, "reviews")
    f.routes["reviews"] = "new"
    ask(f, "reviews")

    print("5) 문제가 생기면 되돌리기도 한 줄")
    f.routes["reviews"] = "legacy"
    ask(f, "reviews")
    f.routes["reviews"] = "new"

    print("6) 지금 길 안내표")
    for name, where in f.routes.items():
        print(f"   {name:<8} -> {where}")
    print(f"   레거시에 남은 일: {[n for n, w in f.routes.items() if w == 'legacy']}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
