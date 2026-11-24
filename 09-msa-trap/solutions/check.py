"""연습 문제 풀이: 결제를 동기 호출 대신 이벤트로 받게 바꾸면 사슬이 얼마나 짧아지나."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from trap import diagnose, load  # noqa: E402

cfg = load(Path(__file__).resolve().parents[1] / "distributed.json")
cfg["calls"]["stock"] = []  # stock -> payment 동기 호출을 「결제됨」 이벤트 구독으로 바꿈
print("사슬:", diagnose(cfg)["chains"] or "2홉 이하")
cfg["dbs"]["stock"] = "stock_db"  # 재고 표를 자기 DB로 옮김
print("공유 DB:", diagnose(cfg)["shared"] or "없음")
