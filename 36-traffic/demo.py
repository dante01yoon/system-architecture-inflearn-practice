"""신간 출간일, 트래픽이 10배로 몰릴 때: 1 = 먼저 재기, 2 = 하나씩 고치기."""
import sys
import unicodedata

from sim import MAX_CONN, NORMAL, SPIKE, SPIKE_FROM, SPIKE_TO, run


def pad(text, width, right=False):
    """한글은 두 칸으로 세어 빈칸을 채운다(표 줄 맞춤). right=True면 오른쪽 정렬."""
    gap = ' ' * (width - sum(2 if unicodedata.east_asian_width(c) in 'WF' else 1 for c in text))
    return gap + text if right else text + gap


def measure():
    r = run()
    total = r['reads'] + r['writes']
    print(f"신간 출간: 평소 초당 {NORMAL}건 → {SPIKE_TO - SPIKE_FROM}초 동안 초당 {SPIKE:,}건 (10배)")
    print("1) 고치기 전에 먼저 재기")
    print(f"   요청 {total:,.0f}건 · 읽기 {r['reads'] / total:.0%} · 쓰기 {r['writes'] / total:.0%}")
    print(f"   {pad('단계', 14)}사용률(최대)  줄에서 기다린 시간(최대)")
    for name, k in [('앱 서버 4대', 'app'), ('DB', 'db')]:
        print(f"   {pad(name, 14)}{r[k + '_use']:>10.0%}  {r[k + '_wait'] / 1000:>14.1f}초")
    share = r['in_db'] / (r['in_app'] + r['in_db'])
    print(f"   응답 시간이 쓰인 곳: 앱 {1 - share:.2%} · DB {share:.2%}")
    where = 'DB' if r['db_wait'] > r['app_wait'] else '앱 서버'
    print(f"   p95 {r['p95'] / 1000:.1f}초 → 줄이 쌓이는 곳은 {where}")


def fix():
    steps = [('그대로 (앱 4대 · 풀 15)', {}),
             ('① 앱 서버 4 → 8대', {'servers': 8}),
             ('② + 읽기 캐시 (적중 90%)', {'servers': 8, 'hit': 0.9}),
             ('③ + 풀 15 → 12 (연결 96)', {'servers': 8, 'hit': 0.9, 'pool': 12})]
    print(f"2) 하나씩 고치기 · DB 연결 한도 {MAX_CONN}")
    print(f"   {pad('고친 것', 28)}{'p95':>7}  DB 사용률  연결 오류")
    base = None
    for name, kw in steps:
        r = run(**kw)
        base = base or r['db_use']
        p95 = f"{r['p95'] / 1000:.1f}초" if r['p95'] >= 1000 else f"{r['p95']:.0f}ms"
        print(f"   {pad(name, 28)}{pad(p95, 7, True)}  {r['db_use']:>8.0%}  {r['errors']:>8,.0f}")
    print(f"   DB가 할 일: {base:.0%} → {r['db_use']:.0%} ({1 - r['db_use'] / base:.0%} 줄어듦)")


if __name__ == "__main__":
    {'1': measure, '2': fix}.get(sys.argv[1] if len(sys.argv) > 1 else '1')()
