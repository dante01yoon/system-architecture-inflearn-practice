"""연습 문제 풀이: 10장 품질 시나리오 표에서 「측정」 칸이 빈 줄을 찾는다."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arc42 import split  # noqa: E402


def missing_measure(text):
    rows = [r.strip().strip("|").split("|") for r in split(text).get(10, "").splitlines() if r.startswith("|")]
    head, data = rows[0], rows[2:]
    k = [c.strip() for c in head].index("측정")
    return [r[0].strip() for r in data if not r[k].strip()]


if __name__ == "__main__":
    doc = Path(__file__).resolve().parents[1] / "bookshop/arc42.md"
    text = doc.read_text(encoding="utf-8") + "\n"
    text = text.replace("## 11.", "| 쿠폰 추가 | 새 쿠폰 종류 | 개발 중 | 플러그인 추가 | |\n\n## 11.")
    assert missing_measure(text) == ["쿠폰 추가"]
    print("측정이 빈 시나리오:", missing_measure(text))
