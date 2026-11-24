"""영상 올리기 뒤쪽을 작게: 조각 나누기 · 변환 작업 그래프(DAG)와 일꾼 · HLS 비슷한 재생 목록 · 화질 고르기(ABR)."""
import heapq
import random

# 화질 사다리: Apple HLS 저작 규격의 H.264 예시 값(16:9) 중 세 줄 · kbit/s
RENDITIONS = [("360p", "640x360", 365), ("720p", "1280x720", 3000), ("1080p", "1920x1080", 6000)]
COST = {"360p": 0.3, "720p": 0.8, "1080p": 1.5}   # 영상 1초를 바꾸는 데 걸리는 초(가정)


def split(duration, seg=4.0):
    """원본 길이를 seg초 조각으로. 마지막 조각은 짧을 수 있다."""
    out, t = [], 0.0
    while t < duration:
        out.append(round(min(seg, duration - t), 3))
        t += seg
    return out


def build_dag(segs):
    """작업 이름 → (걸리는 초, 먼저 끝나야 할 작업들)."""
    dag = {"inspect": (1.0, []), "split": (2.0, ["inspect"])}
    for name, _, _ in RENDITIONS:
        parts = []
        for i, s in enumerate(segs):
            parts.append(f"{name}/{i}")
            dag[f"{name}/{i}"] = (s * COST[name], ["split"])
        dag[f"pack/{name}"] = (0.5, parts)
    dag["master"] = (0.2, [f"pack/{n}" for n, _, _ in RENDITIONS])
    return dag


def run(dag, workers, seed=7):
    """일꾼이 준비된 작업을 큐에서 꺼낸다. 시간은 계산만, ±20% 흔들림."""
    rnd = random.Random(seed)
    took = {k: round(c * rnd.uniform(0.8, 1.2), 3) for k, (c, _) in sorted(dag.items())}
    waiting = {k: set(d) for k, (_, d) in dag.items()}
    ready = sorted(k for k, d in waiting.items() if not d)
    free, busy, done, t, order = workers, [], {}, 0.0, []
    while ready or busy:
        while free and ready:
            k = ready.pop(0)
            heapq.heappush(busy, (t + took[k], k)); free -= 1
        t, k = heapq.heappop(busy); free += 1
        done[k] = t; order.append(k)
        for j, d in waiting.items():
            if k in d:
                d.discard(k)
                if not d and j not in done and j not in ready and all(j != b for _, b in busy):
                    ready.append(j)
    return round(t, 1), order, round(sum(took.values()), 1)


def media_playlist(segs, name):
    lines = ["#EXTM3U", "#EXT-X-VERSION:3",
             f"#EXT-X-TARGETDURATION:{int(max(segs) + 0.999)}",
             "#EXT-X-MEDIA-SEQUENCE:0", "#EXT-X-PLAYLIST-TYPE:VOD"]
    for i, s in enumerate(segs):
        lines += [f"#EXTINF:{s:.3f},", f"{name}/seg{i}.ts"]
    return lines + ["#EXT-X-ENDLIST"]


def master_playlist():
    lines = ["#EXTM3U"]
    for name, res, kbps in RENDITIONS:
        lines += [f"#EXT-X-STREAM-INF:BANDWIDTH={kbps * 1000},RESOLUTION={res}", f"{name}.m3u8"]
    return lines


def choose(kbps_estimate, safety=0.8):
    """측정한 대역폭의 80% 안에 드는 가장 높은 화질(없으면 가장 낮은 것)."""
    fit = [r for r in RENDITIONS if r[2] <= kbps_estimate * safety]
    return (fit or RENDITIONS[:1])[-1]


def play(trace, seg=4.0, fixed=None):
    """조각마다 화질을 고르고 받는다. 버퍼가 바닥나면 그만큼 기다린다."""
    buffer, stall, rows, est = 0.0, 0.0, [], 0   # 처음엔 가장 낮은 화질
    for bw in trace:
        r = fixed or choose(est)
        dl = r[2] * seg / bw                       # 받는 데 걸린 초 = 조각 크기 ÷ 실제 대역폭
        wait = max(0.0, dl - buffer)
        stall += wait
        buffer = max(0.0, buffer - dl) + seg
        rows.append((bw, r[0], round(dl, 1), round(wait, 1)))
        est = bw                                   # 다음 조각은 방금 잰 값으로
    return rows, round(stall, 1)


def trace(n=8, seed=7):
    """대역폭 기록(kbit/s): 처음엔 넉넉 → 엘리베이터에서 뚝 → 회복. seed로 고정."""
    rnd = random.Random(seed)
    base = [9000, 8000, 7000, 2500, 1200, 2000, 6000, 9000][:n]
    return [int(b * rnd.uniform(0.9, 1.1)) for b in base]
