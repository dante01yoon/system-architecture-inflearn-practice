"""연습 문제 풀이: 같은 층의 pricing과 storage가 서로 모르게(import-linter의 independence 계약과 같은 생각)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import fitness  # noqa: E402

INDEPENDENT = ["bookshop.pricing", "bookshop.storage"]


def tangled(g):
    return [f"{a} -> {b}" for a in INDEPENDENT for b in g.get(a, {}) if b in INDEPENDENT]


if __name__ == "__main__":
    bad = tangled(fitness.graph(sys.argv[1] if len(sys.argv) > 1 else ROOT))
    print("[FAIL] independence " + "; ".join(bad) if bad else "[PASS] independence pricing ⟂ storage")
    sys.exit(1 if bad else 0)
