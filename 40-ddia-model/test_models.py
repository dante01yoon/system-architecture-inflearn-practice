import unittest

import document
import graph
import relational

X, NEW = 'Martin Fowler', '마틴 파울러'


class ModelsTest(unittest.TestCase):
    def setUp(self):
        self.db, self.st, self.g = relational.build(), document.build(), graph.build()

    def test_order_7_is_same_in_all_models(self):
        want = [('Designing Data-Intensive Applications', 1, 52000), ('NoSQL Distilled', 2, 30000)]
        self.assertEqual(relational.order(self.db, 7), want)
        self.assertEqual(document.order(self.st, 7), want)
        self.assertEqual(graph.order(self.g, 7), want)

    def test_coauthor_books_agree_and_exclude_own_books(self):
        r = relational.coauthor_books(self.db, X)
        self.assertEqual(r, document.coauthor_books(self.st, X)[0])
        self.assertEqual(r, graph.coauthor_books(self.g, X)[0])
        self.assertIn('Refactoring Databases', r)
        self.assertNotIn('NoSQL Distilled', r)  # Fowler 자신의 책은 빠진다
        self.assertNotIn('Designing Data-Intensive Applications', r)  # 공저자가 아닌 사람의 책

    def test_rename_touches_one_row_but_many_documents(self):
        self.assertEqual(relational.rename(self.db, X, NEW), 1)
        self.assertEqual(relational.order(self.db, 7)[1][0], 'NoSQL Distilled')
        self.assertEqual(relational.coauthor_books(self.db, NEW), relational.coauthor_books(relational.build(), X))
        ch = document.rename(self.st, X, NEW)
        self.assertEqual(ch, {'books': 2, 'orders': 6})
        self.assertEqual(document.stale(self.st, X), 0)

    def test_forgetting_a_collection_leaves_stale_names(self):
        document.rename(self.st, X, NEW, collections=('books',))
        self.assertEqual(document.stale(self.st, X), 6)


if __name__ == '__main__':
    unittest.main()
