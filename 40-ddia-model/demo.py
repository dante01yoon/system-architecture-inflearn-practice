"""같은 서점 데이터를 세 모델로: 1 = 주문 하나 꺼내기, 2 = 공저자 찾기 · 이름 바꾸기."""
import sys

import document
import graph
import relational

X, NEW = 'Martin Fowler', '마틴 파울러'


def part1():
    db, st, g = relational.build(), document.build(), graph.build()
    rows = sum(db.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]
               for t in ('authors', 'books', 'book_authors', 'orders', 'order_items'))
    print('1) 같은 서점 데이터, 세 가지 모델')
    print(f'   관계형  테이블 5개 · 행 {rows}개')
    print(f"   문서형  문서 {len(st['books']) + len(st['orders'])}개 (책 {len(st['books'])} · 주문 {len(st['orders'])})")
    print(f'   그래프  노드 {len(g[0])}개 · 간선 {sum(len(v) for v in g[1].values())}개')
    print('2) 주문 #7과 항목 꺼내기')
    print(f'   관계형  SQL 1번 · 테이블 3개를 조인 {relational.joins(relational.ORDER_SQL)}번')
    print('   문서형  문서 1개 읽기 · 조인 없음')
    print(f"   그래프  주문 노드에서 간선 {len(g[1]['o7'])}개 따라가기")
    items = document.order(st, 7)
    assert items == relational.order(db, 7) == graph.order(g, 7)
    print(f'   → 주문 #7: {sum(q for _, q, _ in items)}권 · {sum(q * p for _, q, p in items):,}원')
    for t, q, _ in items:
        print(f'     - {t} × {q}')


def part2():
    db, st, g = relational.build(), document.build(), graph.build()
    print(f'3) {X}와 함께 쓴 저자들의 다른 책')
    r = relational.coauthor_books(db, X)
    d, scanned = document.coauthor_books(st, X)
    gr, walked = graph.coauthor_books(g, X)
    assert r == d == gr
    print(f'   관계형  SQL 1번 · 조인 {relational.joins(relational.COAUTHOR_SQL)}번')
    print(f'   문서형  책 문서 {scanned}개 전부 훑기')
    print(f'   그래프  간선 {walked}개 따라가기')
    for t in r:
        print(f'     - {t}')
    print(f'4) 저자 이름 바꾸기: {X} → {NEW}')
    print(f'   관계형  행 {relational.rename(db, X, NEW)}개 고침')
    print(f'   그래프  노드 {graph.rename(g, X, NEW)}개 고침')
    ch = document.rename(st, X, NEW)
    print(f"   문서형  문서 {sum(ch.values())}개 고침 (책 {ch['books']} · 주문 {ch['orders']})")
    miss = document.build()
    document.rename(miss, X, NEW, collections=('books',))
    print(f'   문서형  주문 문서를 빠뜨리면 → 옛 이름이 {document.stale(miss, X)}곳에 남음')


if __name__ == '__main__':
    {'1': part1, '2': part2}.get(sys.argv[1] if len(sys.argv) > 1 else '', lambda: (part1(), part2()))()
