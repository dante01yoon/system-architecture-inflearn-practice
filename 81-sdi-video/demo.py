"""python3 demo.py 1 → 조각과 변환 작업 그래프,  2 → 재생 목록,  3 → 화질 고르기(ABR)"""
import sys
from pathlib import Path

from video import RENDITIONS, build_dag, master_playlist, media_playlist, play, run, split, trace

DURATION = 30.0   # 예제 원본 길이(초)


def pipeline():
    segs = split(DURATION)
    print(f"1) 원본 {DURATION:.0f}초 → 4초 조각 {len(segs)}개 (마지막 {segs[-1]:.0f}초)")
    dag = build_dag(segs)
    n = sum(1 for k in dag if "/" in k and not k.startswith("pack"))
    print(f"2) 작업 그래프: 검사 1 → 나누기 1 → 변환 {n}개 (화질 {len(RENDITIONS)} × 조각 {len(segs)}) → 묶기 {len(RENDITIONS)} → 마스터 1")
    print(f"   작업 모두 {len(dag)}개 · 화질: " + " · ".join(f"{a} {c:,}kbps" for a, _, c in RENDITIONS))
    print("3) 일꾼 수에 따라 끝나는 시각 (seed 7)")
    for w in (1, 4, 12, 24):
        end, order, total = run(dag, w)
        print(f"   일꾼 {w:>2}명  →  {end:>5.1f}초")
    print(f"   일 전체 합 {total}초 · 마지막 작업 = {order[-1]}")
    end, order, _ = run(dag, 4)
    print(f"4) 일꾼 4명일 때 먼저 끝난 묶기: {[k for k in order if k.startswith('pack')][0]}")


def playlists():
    segs = split(DURATION)
    out = Path("out"); out.mkdir(exist_ok=True)
    m = master_playlist()
    (out / "master.m3u8").write_text("\n".join(m) + "\n")
    for name, _, _ in RENDITIONS:
        (out / f"{name}.m3u8").write_text("\n".join(media_playlist(segs, name)) + "\n")
    print("1) out/master.m3u8 — 화질 목록")
    for line in m:
        print("   " + line)
    med = media_playlist(segs, "360p")
    print(f"2) out/360p.m3u8 — 조각 목록 (모두 {len(med)}줄 중 앞 7줄)")
    for line in med[:7]:
        print("   " + line)
    print("3) 끝 3줄: " + "  ".join(med[-3:]))


def abr():
    tr = trace()
    rows, stall = play(tr)
    print("1) 조각마다 잰 대역폭 → 고른 화질 (앞 조각 기준 · 80%만 믿기 · 처음엔 가장 낮게)")
    print("   조각  대역폭      화질   받기   기다림")
    for i, (bw, name, dl, wait) in enumerate(rows):
        print(f"   {i:>3}  {bw:>5,}kbps  {name:<5}  {dl:>4}초  {wait}초")
    switches = sum(1 for a, b in zip(rows, rows[1:]) if a[1] != b[1])
    print(f"2) ABR: 화질 바뀜 {switches}번 · 기다림 모두 {stall}초")
    _, fixed = play(tr, fixed=RENDITIONS[-1])
    print(f"3) 1080p로 고정하면: 기다림 모두 {fixed}초")


if __name__ == "__main__":
    {"1": pipeline, "2": playlists, "3": abr}[sys.argv[1] if len(sys.argv) > 1 else "1"]()
