"""python3 demo.py 1 → 선형성 검사,  2 → 2단계 커밋에서 코디네이터가 멈추면,  3 → 5대가 3|2로 갈라졌을 때 과반 선거"""
import sys

from election import Node, elect
from linear import check, op
from twopc import Coordinator, Participant, try_update


def one():
    for i, (name, last) in enumerate([("기록 A", 4), ("기록 B", 5)], 1):
        h = [op("민지", "write", 4, 0, 10), op("준호", "read", 5, 5, 12), op("아라", "read", last, 20, 25)]
        print(f"{i}. {name} (처음 재고 5권)")
        print("   민지 쓰기 재고 4권    0~10ms")
        print("   준호 읽기 재고 5권    5~12ms (쓰기와 겹침)")
        print(f"   아라 읽기 재고 {last}권   20~25ms (쓰기가 끝난 뒤 시작)")
        order = check(h, initial=5)
        print(f"   선형성 통과, 한 줄 순서: {', '.join(order)}" if order else "   선형성 실패: 쓰기가 끝난 뒤 시작한 읽기가 옛 값")


def two():
    stock, pay = Participant("재고"), Participant("결제")
    c = Coordinator([stock, pay])
    c.run(crash_after_decision=True)
    print("1. 코디네이터가 묻기: 준비됐나요?")
    print(f"   재고 DB 예, 결제 DB 예 {'(둘 다 잠금을 걸고 기다림)' if stock.locked and pay.locked else ''}")
    print(f"2. 코디네이터가 로그에 {c.log[-1]}을 적고 알리기 전에 멈춤")
    print(f"3. 재고 DB 상태 {stock.state}, 결제 DB 상태 {pay.state}: 혼자 정할 수 없음")
    print(f"4. 다른 주문이 같은 책 재고 바꾸기 → {try_update(stock)}")
    c.recover()
    print(f"5. 코디네이터 복구, 로그대로 {c.log[-1]} 알림 → 재고 {stock.state}, 결제 {pay.state}")
    print(f"   잠금 풀림 → 다른 주문 {try_update(stock)}")


def three():
    nodes = {n: Node(n) for n in "ABCDE"}
    big, small = [nodes[n] for n in "ABC"], [nodes[n] for n in "DE"]
    print(f"1. 노드 5대, 과반은 {len(nodes) // 2 + 1}표")
    print("2. 네트워크가 갈라짐: A B C 쪽 3대, D E 쪽 2대")
    votes, won = elect(nodes["A"], 2, big, len(nodes))
    print(f"3. A 쪽 선거 임기 2: 표 {' '.join(votes)}, {len(votes)}표 → {'A가 리더' if won else '리더 없음'}")
    votes, won = elect(nodes["D"], 2, small, len(nodes))
    print(f"4. D 쪽 선거 임기 2: 표 {' '.join(votes)}, {len(votes)}표 → {'D가 리더' if won else '리더 없음'}")
    votes, won = elect(nodes["D"], 3, small, len(nodes))
    print(f"5. D 쪽 다시 임기 3: {len(votes)}표 → {'D가 리더' if won else '또 리더 없음'}")
    print("   리더는 많아야 한 쪽에만: 스플릿 브레인이 생기지 않음")


if __name__ == "__main__":
    {"1": one, "2": two, "3": three}[sys.argv[1] if len(sys.argv) > 1 else "1"]()
