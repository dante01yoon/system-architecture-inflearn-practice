"""그래프: 점(노드)과 점을 잇는 선(간선). 선마다 이름이 있다(WROTE, HAS)."""
from collections import defaultdict

from shop import AUTHORS, BOOKS, ORDERS


def build():
    nodes, out, inn = {}, defaultdict(list), defaultdict(list)

    def edge(a, label, b, qty=None):
        out[a].append((label, b, qty)); inn[b].append((label, a, qty))
    for a, name in AUTHORS.items():
        nodes[f'a{a}'] = {'label': 'Author', 'name': name}
    for b, (title, authors, price) in BOOKS.items():
        nodes[f'b{b}'] = {'label': 'Book', 'title': title, 'price': price}
        for a in authors:
            edge(f'a{a}', 'WROTE', f'b{b}')
    for o, (cust, items) in ORDERS.items():
        nodes[f'o{o}'] = {'label': 'Order', 'customer': cust}
        for b, q in items:
            edge(f'o{o}', 'HAS', f'b{b}', q)
    return nodes, out, inn


def order(g, oid):
    nodes, out, _ = g
    return [(nodes[b]['title'], q, nodes[b]['price']) for _, b, q in out[f'o{oid}']]


def coauthor_books(g, name):
    nodes, out, inn = g
    walked = 0
    x = next(n for n, p in nodes.items() if p.get('name') == name)
    mine = [b for _, b, _ in out[x]]
    co = set()
    for b in mine:                      # 내 책 ← 함께 쓴 사람
        for label, a, _ in inn[b]:
            walked += 1
            if label == 'WROTE':
                co |= {a} - {x}
    found = set()
    for a in co:                        # 그 사람 → 그 사람의 책
        for _, b, _ in out[a]:
            walked += 1
            found |= {b} - set(mine)
    return sorted(nodes[b]['title'] for b in found), walked


def rename(g, old, new):
    for p in g[0].values():
        if p.get('name') == old:
            p['name'] = new
            return 1
