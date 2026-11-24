"""패키지 안 모듈끼리 누가 누구를 import 하는지 세어 결합도를 보여 준다.

python3 coupling.py shop_tight
"""
import ast
import sys
from pathlib import Path


def imports(pkg):
    """모듈 이름 -> 그 모듈이 import하는 같은 패키지 모듈들. 조립만 하는 __init__.py는 세지 않는다."""
    pkg = Path(pkg)
    mods = {p.stem for p in pkg.glob("*.py") if p.stem != "__init__"}
    graph = {}
    for m in sorted(mods):
        used = set()
        for node in ast.walk(ast.parse((pkg / f"{m}.py").read_text(encoding="utf-8"))):
            # shortcut: 절대 import만 센다. 상대 import(from . import a)가 있으면 여기에 더한다
            if isinstance(node, ast.ImportFrom) and node.module == pkg.name:
                used |= {a.name for a in node.names}
            elif isinstance(node, ast.ImportFrom) and (node.module or "").startswith(pkg.name + "."):
                used.add(node.module.split(".")[1])
            elif isinstance(node, ast.Import):
                used |= {a.name.split(".")[1] for a in node.names if a.name.startswith(pkg.name + ".")}
        graph[m] = (used & mods) - {m}
    return graph


def dependents(graph, target):
    """target을 바로 import하는 모듈들, 그리고 거쳐서라도 target에 닿는 모듈들."""
    direct = {m for m, deps in graph.items() if target in deps}
    reach, todo = set(), [target]
    while todo:
        t = todo.pop()
        for m, deps in graph.items():
            if t in deps and m != target and m not in reach:
                reach.add(m)
                todo.append(m)
    return direct, reach


def show(graph):
    for m, deps in graph.items():
        print(f"   {m:<8} -> {', '.join(sorted(deps)) or '(없음)'}")
    print(f"   화살표 {sum(len(d) for d in graph.values())}개")


if __name__ == "__main__":
    show(imports(sys.argv[1] if len(sys.argv) > 1 else "shop_tight"))
