"""작은 LSM-tree: 쓰기는 로그 끝에 덧붙이고, 메모리 표(memtable)가 차면 정렬해 세그먼트 파일로 내린다."""
from bisect import bisect_left
from pathlib import Path


class LSM:
    def __init__(self, folder, limit=1500, merge_at=4):
        self.dir, self.limit, self.merge_at = Path(folder), limit, merge_at
        self.mem, self.segs, self.written, self.n = {}, [], 0, 0
        self.wal = open(self.dir / 'wal.log', 'ab')

    def put(self, key, value):
        rec = f'{key}\t{value}\n'.encode()
        self.wal.write(rec)                   # 1. 먼저 WAL에 덧붙이기(전원이 나가도 복구)
        self.written += len(rec)
        self.mem[key] = value                 # 2. 메모리 표에 넣기
        if len(self.mem) >= self.limit:
            self.flush()

    def flush(self):
        self.segs.append(self._write(sorted(self.mem.items())))   # 정렬해서 파일 하나로
        self.mem = {}
        self.wal.truncate(0)                  # 파일에 내렸으니 로그는 비운다
        if len(self.segs) >= self.merge_at:
            self.compact()

    def compact(self):
        merged = {}
        for keys, values, path in self.segs:  # 오래된 것부터 → 새 값이 덮어쓴다
            merged.update(zip(keys, values))
            path.unlink()
        self.segs = [self._write(sorted(merged.items()))]

    def get(self, key):
        if key in self.mem:
            return self.mem[key], 0
        touched = 0
        for keys, values, _ in reversed(self.segs):  # 새 세그먼트부터
            touched += 1
            i = bisect_left(keys, key)
            if i < len(keys) and keys[i] == key:
                return values[i], touched
        return None, touched

    def _write(self, items):
        self.n += 1
        path = self.dir / f'seg{self.n:03d}.sst'
        data = ''.join(f'{k}\t{v}\n' for k, v in items).encode()
        path.write_bytes(data)
        self.written += len(data)
        # shortcut: 읽기는 메모리에 둔 정렬 사본으로 한다(파일 수만 센다). 실제 엔진은 블록 인덱스로 파일 일부만 읽는다
        return [k for k, _ in items], [v for _, v in items], path
