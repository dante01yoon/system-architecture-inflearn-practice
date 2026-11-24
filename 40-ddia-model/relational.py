"""관계형: 같은 값은 한 곳에만, 나머지는 번호(ID)로 가리킨다."""
import sqlite3

from shop import AUTHORS, BOOKS, ORDERS


def build():
    db = sqlite3.connect(':memory:')
    db.executescript('''
        CREATE TABLE authors(id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE books(id INTEGER PRIMARY KEY, title TEXT, price INTEGER);
        CREATE TABLE book_authors(book_id INTEGER, author_id INTEGER);
        CREATE TABLE orders(id INTEGER PRIMARY KEY, customer TEXT);
        CREATE TABLE order_items(order_id INTEGER, book_id INTEGER, qty INTEGER);''')
    db.executemany('INSERT INTO authors VALUES (?,?)', AUTHORS.items())
    for b, (title, authors, price) in BOOKS.items():
        db.execute('INSERT INTO books VALUES (?,?,?)', (b, title, price))
        db.executemany('INSERT INTO book_authors VALUES (?,?)', [(b, a) for a in authors])
    for o, (cust, items) in ORDERS.items():
        db.execute('INSERT INTO orders VALUES (?,?)', (o, cust))
        db.executemany('INSERT INTO order_items VALUES (?,?,?)', [(o, b, q) for b, q in items])
    return db


ORDER_SQL = '''
    SELECT b.title, i.qty, b.price FROM orders o
    JOIN order_items i ON i.order_id = o.id
    JOIN books b ON b.id = i.book_id
    WHERE o.id = ?'''


def order(db, oid):
    return db.execute(ORDER_SQL, (oid,)).fetchall()


COAUTHOR_SQL = '''
    SELECT DISTINCT b.title FROM authors x
    JOIN book_authors xa ON xa.author_id = x.id
    JOIN book_authors ca ON ca.book_id = xa.book_id AND ca.author_id != x.id
    JOIN book_authors cb ON cb.author_id = ca.author_id
    JOIN books b ON b.id = cb.book_id
    WHERE x.name = ? AND b.id NOT IN
      (SELECT book_id FROM book_authors WHERE author_id = x.id)
    ORDER BY b.title'''


def coauthor_books(db, name):
    return [t for (t,) in db.execute(COAUTHOR_SQL, (name,))]


def rename(db, old, new):
    return db.execute('UPDATE authors SET name = ? WHERE name = ?', (new, old)).rowcount


def joins(sql):
    return sql.count('JOIN')
