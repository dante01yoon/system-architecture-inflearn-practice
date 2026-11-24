"""의존성 규칙: 안쪽은 바깥을 모른다. 검사기로 어긴 곳을 잡고, 저장소를 바꿔 끼워도 유스케이스는 그대로."""
import hashlib
import shutil
import tempfile
from pathlib import Path

import checker
from bookshop.main import build
from bookshop.usecases import OrderRequest

HERE = Path(__file__).parent
USECASES = HERE / "bookshop/usecases.py"
SHORTCUT = "from bookshop.adapters.sqlite_repo import SqliteBooks\n"


def main():
    print("1) 지금 코드 검사")
    print("  ", checker.check(HERE) or "OK: 모든 import가 안쪽을 향함")

    print("2) 유스케이스에 SQLite 저장소를 바로 import해 보면")
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copytree(HERE / "bookshop", Path(tmp, "bookshop"))
        bad = Path(tmp, "bookshop/usecases.py")
        lines = bad.read_text().splitlines(keepends=True)
        bad.write_text("".join(lines[:5] + [SHORTCUT] + lines[5:]))
        for problem in checker.check(tmp):
            print("   실패:", problem, "(안쪽 → 바깥)")
        bad.write_text("".join(lines))
        print("   그 줄을 지우고 다시:", checker.check(tmp) or "OK")

    print("3) 같은 유스케이스, 저장소만 바꿔 끼우기")
    before = hashlib.sha256(USECASES.read_bytes()).hexdigest()[:8]
    for kind in ["memory", "sqlite"]:
        place = build(kind)
        for n in ["2권", "또 2권"]:
            r = place(OrderRequest("9780134494166", 2))
            print(f"   {type(place.books).__name__:<11} {n:<4} ok={r.ok} total={r.total} left={r.left}")
    print(f"   usecases.py 지문 {before} -> {hashlib.sha256(USECASES.read_bytes()).hexdigest()[:8]} (그대로)")


if __name__ == "__main__":
    main()
