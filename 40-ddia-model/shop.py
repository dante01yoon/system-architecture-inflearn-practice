"""온라인 서점 데이터 하나(책·저자는 실제 출간 정보, 가격·주문은 예제용)."""
AUTHORS = {1: 'Martin Fowler', 2: 'Kent Beck', 3: 'Pramod Sadalage', 4: 'Scott Ambler',
           5: 'Neal Ford', 6: 'Mark Richards', 7: 'Martin Kleppmann', 8: 'Chris Riccomini'}
BOOKS = {  # 책 번호: (제목, 저자 번호들, 가격)
    101: ('Planning Extreme Programming', [2, 1], 28000),
    102: ('NoSQL Distilled', [3, 1], 30000),
    103: ('Test-Driven Development', [2], 33000),
    104: ('Extreme Programming Explained', [2], 31000),
    105: ('Refactoring Databases', [4, 3], 42000),
    106: ('Software Architecture: The Hard Parts', [5, 6, 3], 45000),
    107: ('Fundamentals of Software Architecture', [6, 5], 40000),
    108: ('Designing Data-Intensive Applications', [7, 8], 52000),
}
ORDERS = {  # 주문 번호: (손님, [(책 번호, 권수), …])
    1: ('c-101', [(108, 1)]), 2: ('c-102', [(102, 1), (103, 1)]), 3: ('c-103', [(107, 2)]),
    4: ('c-104', [(101, 1)]), 5: ('c-105', [(106, 1), (102, 1)]), 6: ('c-106', [(104, 1)]),
    7: ('c-107', [(108, 1), (102, 2)]), 8: ('c-108', [(105, 1)]), 9: ('c-109', [(101, 1), (103, 1)]),
    10: ('c-110', [(107, 1)]), 11: ('c-111', [(102, 1)]), 12: ('c-112', [(106, 1)]),
}
