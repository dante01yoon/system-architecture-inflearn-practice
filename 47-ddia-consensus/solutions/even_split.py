"""연습 풀이: 노드 4대가 2|2로 갈라지면 어느 쪽도 과반(3표)을 못 얻는다 — 그래서 노드 수는 홀수로 둔다.
python3 solutions/even_split.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from election import Node, elect  # noqa: E402

for total, sides in ((4, ("AB", "CD")), (5, ("ABC", "DE"))):
    nodes = {k: Node(k) for k in "".join(sides)}
    won = [elect(nodes[s[0]], 1, [nodes[k] for k in s], total)[1] for s in sides]
    print(f"{total}대, {'|'.join(sides)}: 리더가 생긴 쪽 {sum(won)}개 (과반 {total // 2 + 1}표, 견디는 고장 {(total - 1) // 2}대)")
