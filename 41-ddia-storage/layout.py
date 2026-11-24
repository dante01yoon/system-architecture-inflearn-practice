"""줄 단위(row) 대 칸 단위(column) 저장: 같은 주문 표를 두 방식으로 파일에 쓰고, 「가격 합계」를 읽는 바이트를 센다."""
import random
import struct
from array import array
from pathlib import Path

ROW = struct.Struct('<i10siii40s')        # 주문 번호 · 손님 · 책 번호 · 권수 · 가격 · 주소 = 66바이트
PRICES = [28000, 30000, 31000, 33000, 40000, 42000, 45000, 52000]


def make(n=50_000, seed=5):
    rnd = random.Random(seed)
    return [(i, f'c-{rnd.randrange(10000):05d}'.encode(), (b := rnd.randrange(101, 109)), rnd.randint(1, 3),
             PRICES[b - 101], f'Seoul {rnd.randrange(1, 26)}-gu {rnd.randrange(1, 999)}'.encode()) for i in range(n)]


def write_rows(rows, folder):
    path = Path(folder) / 'orders.rows'
    path.write_bytes(b''.join(ROW.pack(*r) for r in rows))
    return path


COLS = ['id', 'customer', 'book', 'qty', 'price', 'address']


def write_columns(rows, folder):
    d = Path(folder)
    for k, name in enumerate(COLS):                          # 칸마다 파일 하나
        col = [r[k] for r in rows]
        if isinstance(col[0], int):
            data = array('i', col).tobytes()                 # 숫자 칸: 4바이트씩
        else:
            data = b''.join(c.ljust(40 if k == 5 else 10, b'\0') for c in col)  # 글자 칸: 고정 폭
        (d / f'{name}.col').write_bytes(data)
    codes = {p: k for k, p in enumerate(PRICES)}            # 사전 압축: 가격 8가지를 1바이트 번호로
    (d / 'price.dict').write_bytes(bytes(codes[r[4]] for r in rows))
    return d


def sum_rows(path):
    data = path.read_bytes()                                 # 줄마다 66바이트를 전부 읽는다
    return sum(r[4] for r in ROW.iter_unpack(data)), len(data)


def sum_column(folder):
    data = (Path(folder) / 'price.col').read_bytes()         # 가격 칸만 읽는다
    return sum(array('i', data)), len(data)


def sum_dict(folder):
    data = (Path(folder) / 'price.dict').read_bytes()        # 번호 1바이트씩 + 사전
    counts = [0] * len(PRICES)
    for c in data:
        counts[c] += 1
    return sum(n * p for n, p in zip(counts, PRICES)), len(data) + 4 * len(PRICES)
