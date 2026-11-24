"""연습 문제 풀이: 대신할 결정 없이 그만 쓰는 결정은 「폐기됨」(Nygard의 deprecated)으로.
실행: python3 solutions/deprecate.py (adr 폴더에서)"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import adr  # noqa: E402


def deprecate(root, n, reason):
    adr.set_status(adr.path(root, n), f"폐기됨\n이유: {reason}")


with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp) / "doc/arch"
    adr.new(root, "주문 메일은 매일 밤 한꺼번에 보낸다")
    adr.accept(root, 1)
    deprecate(root, 1, "주문 확인 메일을 바로 보내기로 하면서 밤 배치를 없앰")
    print("\n".join(adr.listing(root)))
    print(adr.status_of(adr.path(root, 1)))
