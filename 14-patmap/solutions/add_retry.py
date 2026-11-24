"""연습 풀이: 지도에 칸 하나 더 — 잠깐 실패했다가 곧 되는 호출에는 Retry."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import patmap  # noqa: E402

patmap.MAP.insert(3, ("Retry", ["가끔", "잠깐", "다시 하면"],
                      "잠깐 실패했다가 곧 되는 호출", "같은 요청이 두 번 갈 수 있다 · 멱등하게", "Bulkhead·Timeout·재시도"))

if __name__ == "__main__":
    s = "결제 API가 가끔 실패하는데, 다시 하면 돼요"
    assert patmap.find(s)[0][0] == "Retry"
    print("\n".join(patmap.answer(s)))
