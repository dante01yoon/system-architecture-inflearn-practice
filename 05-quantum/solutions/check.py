"""연습 문제 확인: review -> catalog 동기 호출을 더하면 퀀텀이 몇 개?"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from quanta import parse, quanta  # noqa: E402

shop = (Path(__file__).resolve().parents[1] / "shop.txt").read_text(encoding="utf-8")
groups = quanta(*parse(shop + "sync   review   catalog\n"))
print(f"퀀텀 {len(groups)}개: {groups}")
