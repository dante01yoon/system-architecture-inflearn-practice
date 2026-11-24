"""피트니스 함수: 지금 커밋 → 급한 커밋(층 거꾸로) → 느린 커밋 → 고친 커밋. 커밋마다 fitness.py를 CI처럼 돌린다."""
import shutil
import tempfile
from pathlib import Path

import fitness

HERE = Path(__file__).parent
SHORTCUT = "from bookshop.web import render  # 주문 문구를 바로 쓰려고\n"
SLOW = "    import time; time.sleep(0.008)  # 할인 서버에 매번 묻는 셈(8ms)\n"


def commit(title, edit=None, only_fail=True):
    print(title)
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copytree(HERE / "bookshop", Path(tmp, "bookshop"))
        if edit:
            path, line_no, text = edit
            p = Path(tmp, "bookshop", path)
            lines = p.read_text().splitlines(keepends=True)
            p.write_text("".join(lines[:line_no] + [text] + lines[line_no:]))
        fitness.report(tmp, only_fail)


def main():
    commit("1) 지금 커밋", only_fail=False)
    commit("2) 급한 커밋: orders.py가 web을 import", ("orders.py", 3, SHORTCUT))
    commit("3) 느린 커밋: quote가 매번 바깥에 물음", ("pricing.py", 5, SLOW))
    commit("4) 고친 커밋: 두 줄을 되돌림")


if __name__ == "__main__":
    main()
