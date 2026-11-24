"""장난감 Kafka: 파티션 로그(세그먼트 파일), 키 → 파티션, 컨슈머 그룹(오프셋·재조정), 컴팩션."""
import json
import zlib
from pathlib import Path


class Topic:
    def __init__(self, root, name, partitions=3, segment_records=4):
        self.dir = Path(root) / name
        self.n, self.seg = partitions, segment_records
        for p in range(partitions):
            (self.dir / f"p{p}").mkdir(parents=True, exist_ok=True)

    def partition_of(self, key):
        # shortcut: 진짜 Kafka 기본 파티셔너는 murmur2 해시, 여기선 표준 라이브러리 crc32
        return zlib.crc32(key.encode()) % self.n

    def segments(self, p):
        return sorted((self.dir / f"p{p}").glob("*.log"))

    def end_offset(self, p):
        segs = self.segments(p)
        if not segs:
            return 0
        lines = segs[-1].read_text().splitlines()
        return json.loads(lines[-1])["offset"] + 1 if lines else int(segs[-1].stem)

    def append(self, key, value):
        p = self.partition_of(key)
        off = self.end_offset(p)
        segs = self.segments(p)
        # shortcut: 세그먼트를 건수로 자른다(Kafka는 크기·시간, segment.bytes 등)
        if not segs or len(segs[-1].read_text().splitlines()) >= self.seg:
            seg = self.dir / f"p{p}" / f"{off:08d}.log"
        else:
            seg = segs[-1]
        with seg.open("a") as f:  # 끝에 덧붙이기만
            f.write(json.dumps({"offset": off, "key": key, "value": value}, ensure_ascii=False) + "\n")
        return p, off

    def read(self, p, offset, max_records=100):
        out = []
        for seg in self.segments(p):
            for line in seg.read_text().splitlines():
                r = json.loads(line)
                if r["offset"] >= offset:
                    out.append(r)
        return out[:max_records]

    def compact(self, p):
        """키마다 마지막 값만 남긴다. 마지막 세그먼트와 오프셋은 그대로."""
        segs = self.segments(p)
        latest = {}
        for r in self.read(p, 0, 10**9):
            latest[r["key"]] = r["offset"]
        for seg in segs[:-1]:
            recs = [json.loads(line) for line in seg.read_text().splitlines()]
            keep = [r for r in recs if latest[r["key"]] == r["offset"]]
            if keep:
                seg.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in keep))
            else:
                seg.unlink()


class Group:
    """컨슈머 그룹: 파티션 하나는 그룹 안의 컨슈머 하나에게만. 오프셋은 그룹이 파티션마다 기억."""

    def __init__(self, topic, name):
        self.topic, self.name = topic, name
        self.members, self.assignment = [], {}
        self.committed = {p: 0 for p in range(topic.n)}

    def join(self, member):
        self.members.append(member)
        self.rebalance()

    def rebalance(self):
        # 돌아가며 나누기(RoundRobin 방식): p0→첫째, p1→둘째, …
        ms = sorted(self.members)
        self.assignment = {m: [p for p in range(self.topic.n) if ms[p % len(ms)] == m] for m in ms}

    def poll(self, member):
        got = []
        for p in self.assignment[member]:
            recs = self.topic.read(p, self.committed[p])
            got += [(p, r) for r in recs]
            if recs:
                self.committed[p] = recs[-1]["offset"] + 1  # 처리한 뒤 커밋(최소 한 번)
        return got
