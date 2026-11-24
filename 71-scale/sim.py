"""서버 한 대에서 백만 명까지: 칸을 하나씩 더할 때 몇 명까지 버티나. 숫자는 모두 설명을 위해 정한 가정이다."""
DAY, PEAK = 86_400, 3                 # 하루의 초 · 가장 몰릴 때 = 평균 × 3
PAGES, WRITES, FILES = 40, 2, 10      # 한 명이 하루에: 페이지 · 쓰기 · 페이지당 정적 파일
MS = {                                # 요청 하나가 쓰는 시간(밀리초)
    'file': 4, 'page': 50, 'hit': 10, 'write': 50,   # 정적 파일 · 페이지 · 캐시에서 찾은 페이지 · 쓰기
    'heavy': 800, 'db_read': 20, 'db_write': 40,     # 무거운 일(썸네일 · 메일) · DB 읽기 · DB 쓰기
}
CORES, DISK_GB, DATA_MB = 4, 2_000, 2.5  # 서버 한 대 코어 · 디스크 · 한 명이 쌓는 데이터


def per_user(c):
    """사용자 한 명이 가장 몰릴 때 1초에 칸마다 주는 일(밀리초, 디스크는 MB)."""
    page, write = PAGES * PEAK / DAY, WRITES * PEAK / DAY
    hit = c.get('cache', 0)
    app = page * ((1 - hit) * MS['page'] + hit * MS['hit']) + write * MS['write']
    app += 0 if c.get('cdn') else page * FILES * MS['file']
    heavy = write * MS['heavy']
    worker = heavy / PEAK if c.get('queue') else 0      # 큐 뒤 작업자는 평균 속도로만 꺼낸다
    app += 0 if c.get('queue') else heavy
    reads, writes = page * (1 - hit) * MS['db_read'], write * MS['db_write']
    if c.get('split'):
        load = {'앱 서버': app}
        if c.get('replicas'):
            load |= {'DB 주 서버': writes, '읽기 복제본': reads}
        else:
            load['DB'] = reads + writes
    else:
        load = {'서버 한 대': app + reads + writes}
    if worker:
        load['작업자'] = worker
    load['디스크'] = DATA_MB
    return load


def capacity(c):
    """칸마다 버틸 수 있는 양: 대수 × 코어 × 1,000밀리초, 디스크는 GB × 1,000 × 샤드 수."""
    sh = c.get('shards', 1)
    cap = {'서버 한 대': 1, '앱 서버': c.get('apps', 1), 'DB': sh, 'DB 주 서버': sh,
           '읽기 복제본': c.get('replicas', 0) * sh, '작업자': c.get('workers', 0)}
    out = {k: n * CORES * 1000 for k, n in cap.items()}
    out['디스크'] = DISK_GB * 1000 * sh
    return out


def max_users(c):
    """칸마다 버티는 사용자 수와, 가장 먼저 막히는 칸(병목)."""
    cap = capacity(c)
    each = {k: int(cap[k] / v) for k, v in per_user(c).items()}
    neck = min(each, key=each.get)
    return each[neck], neck, each


ADDS = [   # 한 단계에 칸 하나씩
    ('DB 떼어 내기', {'split': 1}),
    ('로드 밸런서 · 앱 서버 16대', {'apps': 16}),
    ('읽기 복제본 2대', {'replicas': 2}),
    ('캐시 적중 80%', {'cache': .8}),
    ('CDN', {'cdn': 1}),
    ('큐 · 작업자 6대', {'queue': 1, 'workers': 6}),
    ('샤드 4개', {'shards': 4}),
]
STEPS = [('서버 한 대', {})]
for name, add in ADDS:
    STEPS.append((name, STEPS[-1][1] | add))   # 앞 단계 설정에 더한다
