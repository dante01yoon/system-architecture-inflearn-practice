"""연습 풀이: 벽시계 대신 램포트 시계(논리 시계)로 도장을 찍으면, 앞 쓰기를 본 뒤의 쓰기가 늘 이긴다.
python3 solutions/lamport_lww.py"""


class Node:
    def __init__(self, name):
        self.name, self.counter = name, 0

    def stamp(self, seen=0):
        self.counter = max(self.counter, seen) + 1   # 본 것 중 가장 큰 번호보다 하나 크게
        return (self.counter, self.name)            # 번호가 같으면 노드 이름으로 순서를 정한다


a, b = Node("A"), Node("B")
w1 = {"value": "36,000원", "stamp": a.stamp()}
w2 = {"value": "32,400원", "stamp": b.stamp(seen=w1["stamp"][0])}   # 관리자2는 36,000원을 본 뒤에 고쳤다
print("1. A의 쓰기 도장", w1["stamp"], "/ B의 쓰기 도장", w2["stamp"])
print("2. 큰 도장이 이김 →", max((w1, w2), key=lambda w: w["stamp"])["value"])
assert max((w1, w2), key=lambda w: w["stamp"])["value"] == "32,400원"
