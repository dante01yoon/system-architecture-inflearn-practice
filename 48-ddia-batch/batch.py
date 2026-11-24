"""온라인 서점 접근 로그로 배치 처리 세 가지: 유닉스식 파이프라인, 맵리듀스, 정렬-병합 조인."""
import hashlib
import random
import zlib
from collections import defaultdict
from pathlib import Path

BOOKS = {1: ("Clean Architecture", 32000), 2: ("Refactoring", 35000), 3: ("Domain-Driven Design", 45000),
         4: ("Building Microservices", 38000), 5: ("Release It!", 30000), 6: ("The Pragmatic Programmer", 33000),
         7: ("Designing Data-Intensive Applications", 48000), 8: ("Accelerate", 25000)}


def make_logs(path, n=10_000, seed=11):
    """접근 로그 한 줄 = 시각 사용자 메서드 경로 상태. 인기 책일수록 자주 열린다."""
    rnd = random.Random(seed)
    with open(path, "w") as f:
        for i in range(n):
            book = rnd.choices(list(BOOKS), weights=[9, 4, 6, 3, 2, 5, 10, 1])[0]
            page = rnd.choice([f"/books/{book}"] * 4 + ["/cart", "/search?q=ddd"])
            ts = f"2026-11-13T{9 + i // 1200:02d}:{i % 60:02d}:{i * 7 % 60:02d}"
            f.write(f"{ts} u{rnd.randint(1, 300):03d} GET {page} 200\n")


# ── 1) 유닉스식: 작은 단계를 파이프로 잇기 (cat | awk | grep | sort | uniq -c | sort -rn | head) ──
def cat(path):
    with open(path) as f:
        yield from f


def field(lines, k):
    return (line.split()[k] for line in lines)


def grep(lines, word):
    return (line for line in lines if word in line)


def uniq_c(sorted_lines):
    last, n = None, 0
    for line in sorted_lines:
        if line != last and n:
            yield n, last
            n = 0
        last, n = line, n + 1
    if n:
        yield n, last


def pipeline(path, top=5):
    return sorted(uniq_c(sorted(grep(field(cat(path), 3), "/books/"))), reverse=True)[:top]


# ── 2) 맵리듀스: map → shuffle(키로 나눠 정렬) → reduce ──
def mapper(line):
    path = line.split()[3]
    if path.startswith("/books/"):
        yield path, 1


def reducer(key, values):
    yield key, sum(values)


def partition(key, n):
    return zlib.crc32(key.encode()) % n


def map_reduce(path, n_map=4, n_reduce=2):
    lines = list(cat(path))
    splits = [lines[i::n_map] for i in range(n_map)]  # 조각 = 파일 블록 대신
    buckets = [defaultdict(list) for _ in range(n_reduce)]
    for split in splits:  # 매퍼마다 자기 조각만 읽는다
        for line in split:
            for k, v in mapper(line):
                buckets[partition(k, n_reduce)][k].append(v)  # 셔플: 같은 키 → 같은 리듀서
    out = []
    for b in buckets:  # 리듀서는 자기 몫을 키 순서로
        for k in sorted(b):
            out += reducer(k, b[k])
    return sorted(((v, k) for k, v in out), reverse=True), [len(b) for b in buckets]


# ── 3) 정렬-병합 조인: 책 번호로 정렬된 두 파일을 나란히 한 번씩만 읽는다 ──
def make_orders(path, n=3000, seed=11):
    rnd = random.Random(seed)
    rows = [(rnd.choice(list(BOOKS)), f"2026-11-{rnd.choice([12, 13]):02d}", rnd.randint(1, 3)) for _ in range(n)]
    with open(path, "w") as f:
        for i, (book, day, qty) in enumerate(sorted(rows), 1):  # 책 번호 순으로 정렬해 둔 입력
            f.write(f"{book}\t{day}\t{qty}\to{i:05d}\n")
    with open(Path(path).with_name("books.tsv"), "w") as f:
        for book, (title, price) in sorted(BOOKS.items()):
            f.write(f"{book}\t{title}\t{price}\n")


def merge_join(orders, books, day):
    o = (line.rstrip("\n").split("\t") for line in cat(orders))
    row = next(o, None)
    for b in (line.rstrip("\n").split("\t") for line in cat(books)):
        n = qty = 0
        while row and row[0] == b[0]:  # 같은 책 번호인 주문을 차례로
            if row[1] == day:
                n, qty = n + 1, qty + int(row[2])
            row = next(o, None)  # 주문 파일은 앞으로만 간다
        yield b[1], n, qty, qty * int(b[2])


def daily_sales(orders, books, day, out_dir, fail_at=None):
    """같은 입력이면 늘 같은 파일. 임시 파일에 다 쓴 뒤 이름을 바꾼다(반쯤 쓴 출력이 남지 않게)."""
    out = Path(out_dir) / f"sales-{day}.tsv"
    tmp = out.with_suffix(".tmp")
    with open(tmp, "w") as f:
        for i, (title, n, qty, won) in enumerate(merge_join(orders, books, day)):
            if i == fail_at:
                raise RuntimeError("작업이 중간에 죽음")
            f.write(f"{title}\t{n}\t{qty}\t{won}\n")
    tmp.replace(out)
    return out


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:12]
