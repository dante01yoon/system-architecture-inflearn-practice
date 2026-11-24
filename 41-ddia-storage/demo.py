"""저장소 엔진 실험: 1 = LSM-tree 대 B-tree(키 5만 개 쓰기·읽기), 2 = 줄 저장 대 칸 저장(가격 합계)."""
import random
import sys
import tempfile
import unicodedata

import layout
from btree import PAGE, BTree
from lsm import LSM

N = 50_000


def workload(seed=7):
    keys = [f'book:{i:06d}' for i in range(N)]
    random.Random(seed).shuffle(keys)                  # 들어오는 순서는 뒤죽박죽
    return [(k, f'title={k[5:]};' + 'x' * 80) for k in keys]


def part1():
    data = workload()
    user = sum(len(f'{k}\t{v}\n'.encode()) for k, v in data)
    print(f'1) 키 {N:,}개 쓰기 · 넣은 데이터 {user / 1e6:.1f}MB')
    lsm, bt = LSM(tempfile.mkdtemp()), BTree()
    for name, db in (('LSM-tree', lsm), ('B-tree', bt)):
        for k, v in data:
            db.put(k, v)
        print(f'   {name:<9} 디스크에 쓴 양 {db.written / 1e6:5.1f}MB · 쓰기 증폭 {db.written / user:4.1f}배')
    print(f'   LSM-tree  세그먼트 파일 {lsm.n}번 씀(합치기 포함) · 남은 파일 {len(lsm.segs)}개 · 메모리 표 {len(lsm.mem):,}개')
    print(f'   B-tree    {PAGE // 1024}KB 페이지 {len(bt.pages):,}장')
    print(f'2) 무작위로 {N:,}번 읽기')
    rnd = random.Random(3)
    probe = [rnd.choice(data)[0] for _ in range(N)]
    for name, db, unit in (('LSM-tree', lsm, '파일'), ('B-tree', bt, '페이지')):
        hops = [db.get(k)[1] for k in probe]
        print(f'   {name:<9} 한 번 읽을 때 {unit} 평균 {sum(hops) / N:.2f}개 · 최대 {max(hops)}개')
    print('3) 없는 키 읽기')
    print(f"   LSM-tree  파일 {lsm.get('book:999999')[1]}개를 다 봐야 「없음」  ·  B-tree  페이지 {bt.get('book:999999')[1]}개")


def pad(text, width):
    return text + ' ' * (width - sum(2 if unicodedata.east_asian_width(c) in 'WF' else 1 for c in text))


def part2():
    rows = layout.make(N)
    d = tempfile.mkdtemp()
    path = layout.write_rows(rows, d)
    layout.write_columns(rows, d)
    print(f'4) 주문 {N:,}줄의 가격 합계 (OLAP 질문)')
    results = [('줄 저장', layout.sum_rows(path)), ('칸 저장', layout.sum_column(d)), ('칸 + 사전 압축', layout.sum_dict(d))]
    base = results[0][1][1]
    for name, (total, nbytes) in results:
        print(f'   {pad(name, 16)}읽은 양 {nbytes / 1e6:5.2f}MB ({nbytes / base:4.0%})  합계 {total:,}원')
    assert len({t for _, (t, _) in results}) == 1
    print('5) 주문 한 건 전부 보기 (OLTP 질문)')
    print(f"   {pad('줄 저장', 16)}파일 1곳에서 {layout.ROW.size}바이트 한 덩어리")
    print(f"   {pad('칸 저장', 16)}칸 파일 {len(layout.COLS)}개에서 한 조각씩 ({len(layout.COLS)}곳)")


if __name__ == '__main__':
    {'1': part1, '2': part2}.get(sys.argv[1] if len(sys.argv) > 1 else '', lambda: (part1(), part2()))()
