"""연습 문제 풀이: 문서에 저자 이름을 복사하지 않고 번호만 넣으면?
이름 바꾸기는 한 곳으로 줄지만, 주문 하나를 보여 주려면 문서를 여러 번 읽어야 한다(앱에서 하는 조인)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from shop import AUTHORS, BOOKS, ORDERS  # noqa: E402

store = {'authors': {a: json.dumps({'name': n}) for a, n in AUTHORS.items()},
         'books': {b: json.dumps({'title': t, 'author_ids': au, 'price': p}) for b, (t, au, p) in BOOKS.items()},
         'orders': {o: json.dumps({'customer': c, 'items': [{'book_id': b, 'qty': q} for b, q in it]}) for o, (c, it) in ORDERS.items()}}
reads = 0


def get(c, k):
    global reads
    reads += 1
    return json.loads(store[c][k])


order = get('orders', 7)
for i in order['items']:
    book = get('books', i['book_id'])
    names = [get('authors', a)['name'] for a in book['author_ids']]
    print(f"- {book['title']} × {i['qty']} ({', '.join(names)})")
print(f'주문 #7을 보여 주는 데 문서 {reads}개 읽음 (이름을 복사해 두면 1개)')
store['authors'][1] = json.dumps({'name': '마틴 파울러'})
print('이름 바꾸기: 저자 문서 1개만 고침')
