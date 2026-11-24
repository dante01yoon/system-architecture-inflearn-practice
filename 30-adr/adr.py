"""ADR(아키텍처 결정 기록) 도구 — Michael Nygard 양식(2011)으로 번호 붙은 마크다운 파일을 만든다.
사용: adr.py new "<제목>" | adr.py accept <번호> | adr.py supersede <번호> "<제목>" | adr.py list"""
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path("doc/arch")  # Nygard 글의 자리: doc/arch/adr-NNN.md
TEMPLATE = """# {n}. {title}

날짜: {day}

## 상태
{status}

## 맥락
(무엇이 부딪히나. 사실만, 가치 판단 없이)

## 결정
(우리는 ~한다)

## 결과
(좋은 것, 나쁜 것, 그냥 달라지는 것 모두)
"""
STATUS = re.compile(r"(## 상태\n)(.*?)(\n\n## )", re.S)


def path(root, n):
    return root / f"adr-{n:03d}.md"


def numbers(root):
    return sorted(int(p.stem[4:]) for p in root.glob("adr-*.md"))


def title_of(p):
    return p.read_text(encoding="utf-8").split("\n", 1)[0].split(". ", 1)[1]


def status_of(p):
    return STATUS.search(p.read_text(encoding="utf-8")).group(2)


def set_status(p, status):
    """상태 칸만 바꾼다. 맥락·결정·결과는 한 번 쓰면 고치지 않는다."""
    text = p.read_text(encoding="utf-8")
    p.write_text(STATUS.sub(lambda m: m.group(1) + status + m.group(3), text, count=1), encoding="utf-8")


def new(root, title, status="제안됨"):
    root.mkdir(parents=True, exist_ok=True)
    n = max(numbers(root), default=0) + 1  # 번호는 늘기만 하고, 지운 번호도 다시 쓰지 않는다
    p = path(root, n)
    p.write_text(TEMPLATE.format(n=n, title=title, day=date.today(), status=status), encoding="utf-8")
    return p


def accept(root, n):
    set_status(path(root, n), "승인됨")


def supersede(root, old, title):
    """old는 상태만 바꾸고 새 결정을 만들어, 두 파일이 서로를 가리키게 한다."""
    old_p = path(root, old)
    if not old_p.exists():
        raise SystemExit(f"없는 결정: {old}")
    new_p = new(root, title, f"제안됨\n대체함: [{old}. {title_of(old_p)}]({old_p.name})")
    set_status(old_p, f"대체됨\n대체한 결정: [{int(new_p.stem[4:])}. {title}]({new_p.name})")
    return new_p


def listing(root):
    return [f"{n:>3}  {status_of(path(root, n)).split(chr(10))[0]}  {title_of(path(root, n))}" for n in numbers(root)]


def main(argv, root=ROOT):
    cmd, *args = argv or ["list"]
    if cmd == "new":
        print(new(root, args[0]))
    elif cmd == "accept":
        accept(root, int(args[0]))
    elif cmd == "supersede":
        print(supersede(root, int(args[0]), args[1]))
    elif cmd == "list":
        print("\n".join(listing(root)))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
