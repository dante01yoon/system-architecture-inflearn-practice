"""서점 피트니스 함수 넷: CI처럼 PASS/FAIL을 찍고, 하나라도 FAIL이면 종료 코드 1."""
import ast
import importlib.util
import sys
import timeit
from pathlib import Path

LAYERS = [["bookshop.web"], ["bookshop.orders"], ["bookshop.pricing", "bookshop.storage"]]  # 위 → 아래
P95_BUDGET_MS = 2.0
MAX_LINES = 40


def graph(root):
    """{모듈: {import한 bookshop 모듈: 줄 번호}} — 코드를 실행하지 않고 ast로 읽는다."""
    g = {}
    for path in sorted(Path(root, "bookshop").glob("[!_]*.py")):
        deps = g.setdefault("bookshop." + path.stem, {})
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("bookshop."):
                deps.setdefault(node.module, node.lineno)
            elif isinstance(node, ast.Import):
                deps.update({a.name: node.lineno for a in node.names if a.name.startswith("bookshop.")})
    return g


def layer(mod):
    return next((i for i, names in enumerate(LAYERS) if mod in names), None)


def upward(g):
    """아래 층이 위 층을 import한 곳들."""
    return [f"{a.split('.')[1]}.py:{line} -> {b}" for a, deps in g.items() for b, line in deps.items()
            if None not in (layer(a), layer(b)) and layer(b) < layer(a)]


def cycle(g):
    """순환 하나를 [a, b, …, a]로, 없으면 None(깊이 우선 탐색)."""
    done, path = set(), []

    def visit(m):
        if m in path:
            return path[path.index(m):] + [m]
        if m in done:
            return None
        path.append(m)
        found = next((c for c in map(visit, g.get(m, {})) if c), None)
        path.pop(); done.add(m)
        return found
    return next((c for c in map(visit, g) if c), None)


def p95_ms(root, runs=100):
    """pricing.quote를 runs번 따로 재서, 느린 쪽 5%가 시작되는 값(밀리초)."""
    spec = importlib.util.spec_from_file_location("pricing_under_test", Path(root, "bookshop/pricing.py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    times = sorted(timeit.repeat(lambda: mod.quote([(32000, 2), (45000, 1)]), number=1, repeat=runs))
    return times[int(runs * 0.95) - 1] * 1000


def run(root="."):
    """[(이름, 통과?, 설명)]"""
    g = graph(root)
    up, cyc, p95 = upward(g), cycle(g), p95_ms(root)
    sizes = {p.name: len(p.read_text().splitlines()) for p in Path(root, "bookshop").glob("*.py")}
    big = max(sizes, key=sizes.get)
    return [
        ("layers", not up, "; ".join(up) or "web → orders → pricing|storage"),
        ("no-cycles", not cyc, " -> ".join(m.split(".")[1] for m in cyc) if cyc else f"모듈 {len(g)}개, 순환 0"),
        ("p95-latency", p95 <= P95_BUDGET_MS, f"quote p95 {p95:.3f}ms (예산 {P95_BUDGET_MS}ms)"),
        ("file-size", sizes[big] <= MAX_LINES, f"가장 큰 {big} {sizes[big]}줄 (한도 {MAX_LINES})"),
    ]


def report(root=".", only_fail=False):
    """CI처럼 찍는다. only_fail이면 FAIL 줄과 합계만."""
    results = run(root)
    for name, ok, detail in results:
        if not (only_fail and ok):
            print(f"   [{'PASS' if ok else 'FAIL'}] {name:<11} {detail}")
    failed = sum(not ok for _, ok, _ in results)
    print(f"   => {len(results) - failed}/{len(results)} PASS" + (" · 머지 막힘" if failed else ""))
    return failed


if __name__ == "__main__":
    sys.exit(1 if report(sys.argv[1] if len(sys.argv) > 1 else ".") else 0)
