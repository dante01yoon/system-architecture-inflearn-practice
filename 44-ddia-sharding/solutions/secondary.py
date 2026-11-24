"""연습 문제 풀이: 「작가007의 주문」을 찾을 때 로컬 인덱스와 글로벌 인덱스가 들르는 샤드 수."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from shard import by_hash, orders  # noqa: E402

SHARDS = 4
data = orders()

# 로컬 인덱스: 샤드마다 「자기 주문」만 작가별로 색인 → 작가로 찾으려면 모든 샤드에 묻는다(scatter/gather)
local = [{} for _ in range(SHARDS)]
for oid, _, author in data:
    local[by_hash(oid, SHARDS)].setdefault(author, []).append(oid)
hits = [s for s in range(SHARDS) if "작가007" in local[s]]
print(f"로컬 인덱스: 샤드 {SHARDS}개 모두에 묻고, 답이 있는 샤드 {len(hits)}개의 결과를 합친다")

# 글로벌 인덱스: 색인 자체를 「작가」로 샤딩 → 작가007 항목은 한 샤드에 모여 있다
glob = [{} for _ in range(SHARDS)]
for oid, _, author in data:
    glob[by_hash(author, SHARDS)].setdefault(author, []).append(oid)
s = by_hash("작가007", SHARDS)
print(f"글로벌 인덱스: 샤드 s{s} 하나에 묻는다 · 주문 {len(glob[s]['작가007'])}건")
print("대가: 주문 하나를 쓰면 주문 샤드와 다른 색인 샤드를 함께 고쳐야 한다(보통 비동기로)")
