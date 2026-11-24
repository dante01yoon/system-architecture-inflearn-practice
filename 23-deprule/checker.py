"""의존성 규칙 검사기: 안쪽 원의 파일이 더 바깥 원을 import하면 실패."""
import ast
import sys
from pathlib import Path

RING = {
    "bookshop.entities": 0,
    "bookshop.usecases": 1,
    "bookshop.adapters": 2,
    "sqlite3": 2,           # DB 드라이버는 어댑터 원부터
    "bookshop.main": 3,
}


def ring(module):
    hits = [r for name, r in RING.items()
            if module == name or module.startswith(name + ".")]
    return hits[0] if hits else None


def imports(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            yield from ((a.name, node.lineno) for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            yield node.module, node.lineno


def check(root):
    bad = []
    for path in sorted(Path(root, "bookshop").rglob("*.py")):
        rel = path.relative_to(root)
        me = ring(".".join(rel.with_suffix("").parts))
        for name, line in imports(ast.parse(path.read_text())):
            if me is not None and ring(name) is not None and ring(name) > me:
                bad.append(f"{rel}:{line} {name}")
    return bad


if __name__ == "__main__":
    problems = check(sys.argv[1] if len(sys.argv) > 1 else ".")
    print("\n".join(problems) or "OK")
    sys.exit(1 if problems else 0)
