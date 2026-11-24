"""배치 처리 실행: 1 = 가장 많이 본 책 다섯 권(파이프라인 대 맵리듀스), 2 = 정렬-병합 조인으로 일별 판매표, 다시 돌려도 같은 결과."""
import shutil
import sys
from pathlib import Path

from batch import BOOKS, daily_sales, make_logs, make_orders, map_reduce, pipeline, sha

W = Path(__file__).resolve().parent / "work"


def name(path):
    return f"#{path.split('/')[-1]} {BOOKS[int(path.split('/')[-1])][0]}"


def top_books():
    shutil.rmtree(W, ignore_errors=True); (W / "input").mkdir(parents=True)
    log = W / "input" / "access.log"
    make_logs(log)
    lines = log.read_text().splitlines()
    print(f"1) 접근 로그 {len(lines):,}줄 (seed 11)")
    print(f"   {next(x for x in lines if '/books/' in x)}")
    print("2) 파이프라인: cat | 4번째 칸 | grep /books/ | sort | uniq -c | sort -rn | head -5")
    top = pipeline(log)
    for n, path in top:
        print(f"   {n:5,}  {name(path)}")
    print("3) 맵리듀스: 입력 4조각 → 매퍼 4개 → 셔플 → 리듀서 2개")
    mr, keys = map_reduce(log)
    print(f"   셔플 뒤 리듀서 1이 받은 책 {keys[0]}종, 리듀서 2가 받은 책 {keys[1]}종")
    print(f"   상위 5: {', '.join(p.split('/')[-1] + '번' for _, p in mr[:5])}")
    print(f"4) 두 결과가 같은가: {'같음' if mr[:5] == top else '다름'}")


def sales():
    shutil.rmtree(W, ignore_errors=True); (W / "input").mkdir(parents=True); (W / "output").mkdir()
    orders, books = W / "input" / "orders.tsv", W / "input" / "books.tsv"
    make_orders(orders)
    before = sha(orders)
    print(f"1) 입력: 주문 {len(orders.read_text().splitlines()):,}줄, 책 {len(BOOKS)}종 — 둘 다 책 번호 순으로 정렬")
    print("2) 정렬-병합 조인: 두 파일을 위에서부터 한 번씩만 읽기")
    out = daily_sales(orders, books, "2026-11-13", W / "output")
    rows = [r.split("\t") for r in out.read_text().splitlines()]
    for title, n, qty, won in rows[:3]:
        print(f"   {title:<22} 주문 {n}건  {qty}권  {int(won):,}원")
    print(f"   … 모두 {len(rows)}줄")
    print(f"3) 출력 work/output/{out.name}  sha256 {sha(out)}")
    first = sha(out)
    out.unlink()
    try:
        daily_sales(orders, books, "2026-11-13", W / "output", fail_at=4)
    except RuntimeError as e:
        print(f"4) 다시 실행했는데 {e}: 출력 파일 {'있음' if out.exists() else '없음'}")
    out = daily_sales(orders, books, "2026-11-13", W / "output")
    print(f"5) 처음부터 또 실행: sha256 {sha(out)} → {'처음과 같음' if sha(out) == first else '다름'}")
    print(f"6) 입력 orders.tsv: {'그대로' if sha(orders) == before else '바뀜'}")


if __name__ == "__main__":
    {"1": top_books, "2": sales}[(sys.argv[1:] or ["1"])[0]]()
