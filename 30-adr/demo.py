"""임시 폴더에서 adr.py를 차례로 실행한다. 인자 show: 대체된 2번 파일을 통째로 본다."""
import contextlib
import io
import sys
import tempfile
from pathlib import Path

import adr

STEPS = [
    ["new", "주문 DB는 PostgreSQL을 쓴다"],
    ["new", "결제 결과를 HTTP로 바로 알린다"],
    ["accept", "1"],
    ["accept", "2"],
    ["supersede", "2", "결제 결과를 아웃박스로 발행한다"],
]


def run(root, argv, tmp):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        adr.main(argv, root)
    return buf.getvalue().strip().replace(tmp + "/", "")


def main(show=False):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "doc/arch"
        for i, argv in enumerate(STEPS, 1):
            out = run(root, argv, tmp)
            if not show:
                shown = " ".join(f'"{a}"' if " " in a else a for a in argv)
                print(f"{i}) adr.py {shown}" + (f"\n   → {out}" if out else ""))
        if show:
            print(adr.path(root, 2).read_text(encoding="utf-8").rstrip())
            return
        print("6) adr.py list")
        print("\n".join("  " + line for line in adr.listing(root)))
        print("7) 바뀐 상태 칸")
        for n in (2, 3):
            first, link = adr.status_of(adr.path(root, n)).split("\n")
            print(f"   adr-00{n}: {first} · {link.split(':')[0]} → {link.split('(')[1].rstrip(')')}")


if __name__ == "__main__":
    main("show" in sys.argv[1:])
