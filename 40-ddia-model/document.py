"""문서형: 한 번에 보는 것을 JSON 문서 하나에 통째로(이름도 복사해 넣는다)."""
import json

from shop import AUTHORS, BOOKS, ORDERS


def build():
    books = {b: json.dumps({'title': t, 'authors': [AUTHORS[a] for a in au], 'price': p})
             for b, (t, au, p) in BOOKS.items()}
    orders = {}
    for o, (cust, items) in ORDERS.items():
        orders[o] = json.dumps({'customer': cust, 'items': [
            {'title': BOOKS[b][0], 'authors': [AUTHORS[a] for a in BOOKS[b][1]],
             'qty': q, 'price': BOOKS[b][2]} for b, q in items]})
    return {'books': books, 'orders': orders}


def order(store, oid):
    doc = json.loads(store['orders'][oid])  # 문서 하나 읽기로 끝
    return [(i['title'], i['qty'], i['price']) for i in doc['items']]


def coauthor_books(store, name):
    docs = [json.loads(d) for d in store['books'].values()]  # 이름으로 이어 줄 곳이 없어 전부 훑는다
    mine = [d for d in docs if name in d['authors']]
    co = {a for d in mine for a in d['authors']} - {name}
    return sorted(d['title'] for d in docs
                  if co & set(d['authors']) and d not in mine), len(docs)


def rename(store, old, new, collections=('books', 'orders')):
    changed = {}
    for c in collections:
        for k, raw in store[c].items():
            if old in raw:  # 복사해 둔 이름을 문서마다 찾아 고친다
                store[c][k] = raw.replace(json.dumps(old), json.dumps(new))
                changed[c] = changed.get(c, 0) + 1
    return changed


def stale(store, old):
    return sum(old in raw for c in store.values() for raw in c.values())
