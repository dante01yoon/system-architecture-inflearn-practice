"""신간 출간일의 온라인 서점: 1초 단위로 앱 → 캐시 → DB를 흘려 보는 모형(숫자는 가정, 무작위 없음)."""
NORMAL, SPIKE = 100, 1000      # 초당 요청: 평소, 출간 직후(10배)
SPIKE_FROM, SPIKE_TO, END = 10, 40, 60
READ_SHARE = 0.95              # 책 페이지 보기 95% · 주문 5%
APP_MS, CACHE_MS = 2, 1        # 요청 하나에 드는 앱 CPU, 캐시 조회
READ_MS, WRITE_MS = 5, 10      # DB에서 책 페이지 읽기, 주문 쓰기
APP_CORES, DB_CORES = 2, 4     # 앱 서버 한 대의 코어, DB 서버의 코어
MAX_CONN = 100                 # DB가 받아 주는 연결 수 한도


def rate(t):
    return SPIKE if SPIKE_FROM <= t < SPIKE_TO else NORMAL


def stage(queue, need, cap):
    """1초 동안 일(ms)이 need만큼 오고 cap만큼 처리된다. 남은 줄과 기다릴 시간(ms)."""
    queue = max(0.0, queue + need - cap)
    return queue, queue / cap * 1000


def run(servers=4, pool=15, hit=0.0):
    """앱 서버 수, 서버마다 DB 연결 풀 크기, 캐시 적중률로 60초를 돌린다."""
    conns = servers * pool
    lost = max(0, conns - MAX_CONN) / conns            # 연결을 못 얻은 몫
    app_q = db_q = 0.0
    r = dict.fromkeys(['reads', 'writes', 'errors', 'in_app', 'in_db',
                       'app_use', 'db_use', 'app_wait', 'db_wait'], 0.0)
    lat = []
    for t in range(END):
        n = rate(t)
        reads, writes = n * READ_SHARE, n * (1 - READ_SHARE)
        hits, misses = reads * hit, reads * (1 - hit)
        r['reads'] += reads
        r['writes'] += writes
        r['errors'] += (misses + writes) * lost        # DB가 필요한데 연결이 없음
        misses, writes = misses * (1 - lost), writes * (1 - lost)

        app_need = n * APP_MS
        db_need = misses * READ_MS + writes * WRITE_MS
        app_cap = servers * APP_CORES * 1000
        db_cap = DB_CORES * 1000
        app_q, app_wait = stage(app_q, app_need, app_cap)
        db_q, db_wait = stage(db_q, db_need, db_cap)

        front = APP_MS + app_wait
        look = CACHE_MS if hit else 0
        lat += [(front + look, hits),
                (front + look + db_wait + READ_MS, misses),
                (front + db_wait + WRITE_MS, writes)]
        r['in_app'] += front * n                       # 응답 시간이 쓰인 곳
        r['in_db'] += (db_wait + READ_MS) * misses + (db_wait + WRITE_MS) * writes
        r['app_use'] = max(r['app_use'], app_need / app_cap)
        r['db_use'] = max(r['db_use'], db_need / db_cap)
        r['app_wait'] = max(r['app_wait'], app_wait)
        r['db_wait'] = max(r['db_wait'], db_wait)
    r['p95'] = percentile(lat, 0.95)
    return r


def percentile(lat, q):
    """(지연 ms, 요청 수) 목록에서 빠른 쪽부터 q만큼 셌을 때의 지연."""
    total, seen = sum(c for _, c in lat), 0.0
    for ms, c in sorted(lat):
        seen += c
        if c and seen >= total * q:
            return ms
