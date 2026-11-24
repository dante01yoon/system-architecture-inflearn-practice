"""B-tree 흉내: 정렬된 페이지(4KB) 목록. 값을 넣을 때마다 그 페이지를 통째로 다시 쓴다."""
from bisect import bisect_right, insort

PAGE = 4096       # 페이지 한 장의 크기(가정)
FANOUT = 200      # 안쪽 페이지 한 장이 가리키는 자식 수(가정: 키 12바이트 + 주소 8바이트)


class BTree:
    def __init__(self, cap=32):
        self.cap, self.firsts, self.pages, self.written = cap, [], [], 0

    def put(self, key, value):
        self.written += len(f'{key}\t{value}\n'.encode())  # WAL은 B-tree도 쓴다
        if not self.pages:
            self.firsts, self.pages = [key], [[]]
        i = max(bisect_right(self.firsts, key) - 1, 0)
        page = self.pages[i]
        insort(page, (key, value))
        self.firsts[i] = page[0][0]
        self.written += PAGE                  # 바뀐 페이지를 통째로 제자리에 다시 쓴다
        if len(page) > self.cap:              # 넘치면 반으로 쪼갠다
            half = len(page) // 2
            self.pages[i:i + 1] = [page[:half], page[half:]]
            self.firsts[i:i + 1] = [page[0][0], page[half][0]]
            self.written += 3 * PAGE          # 새 페이지 둘 + 부모 페이지

    def get(self, key):
        i = max(bisect_right(self.firsts, key) - 1, 0)
        for k, v in self.pages[i]:
            if k == key:
                return v, self.height()
        return None, self.height()

    def height(self):
        """뿌리에서 잎까지 읽는 페이지 수(안쪽 페이지는 FANOUT개씩 가리킨다고 셈)."""
        levels, n = 1, len(self.pages)
        while n > 1:
            n, levels = -(-n // FANOUT), levels + 1
        return levels
