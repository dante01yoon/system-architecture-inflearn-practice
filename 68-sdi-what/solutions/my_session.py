"""연습 문제 풀이: 내 연습 판 답을 넣어 채점하기. 사용: python3 solutions/my_session.py "y n y …"(12개)"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from demo import report  # noqa: E402

if __name__ == "__main__":
    report("내 연습 판", sys.argv[1] if len(sys.argv) > 1 else input("y/n 12개: "))
