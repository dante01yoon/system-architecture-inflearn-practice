"""연습 문제 풀이: 시간대별 접근 수. 매퍼 하나만 바꾸고 셔플·리듀서는 그대로 쓴다."""
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from batch import cat, make_logs, partition, reducer  # noqa: E402


def hour_mapper(line):
    yield line[11:13] + "시", 1          # 2026-11-13T09:… → 09시


def run(path, n_reduce=2):
    buckets = [defaultdict(list) for _ in range(n_reduce)]
    for line in cat(path):
        for k, v in hour_mapper(line):
            buckets[partition(k, n_reduce)][k].append(v)
    return sorted(kv for b in buckets for k in b for kv in reducer(k, b[k]))


if __name__ == "__main__":
    log = Path(tempfile.mkdtemp()) / "access.log"
    make_logs(log)
    for hour, n in run(log):
        print(f"{hour}  {n:5,}")
    assert sum(n for _, n in run(log)) == 10_000
