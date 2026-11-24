# sdi-video — 영상 스트리밍 (파이썬 표준 라이브러리만)

영상이 올라온 뒤의 일을 작게 흉내 낸다. 가짜 원본(30초)을 4초 조각으로 나누고, 화질 세 가지로 바꾸는 작업 그래프(DAG)를 일꾼 여러 명이
큐에서 꺼내 처리하는 시간을 계산하고(seed 7, 실제로 기다리지 않음), HLS 비슷한 마스터 재생 목록과 화질별 재생 목록을 글자로 쓰고,
흔들리는 대역폭 기록 위에서 조각마다 화질을 고르는 ABR을 돌린다. 실제 영상 변환은 하지 않는다.

| 파일 | 역할 |
|---|---|
| `video.py` | `split`(4초 조각), `build_dag`·`run`(작업 그래프 · 일꾼 · 큐), `master_playlist`·`media_playlist`(m3u8 글), `choose`·`play`(대역폭 80% 규칙 · 버퍼 · 기다림), `trace`(seed 7 대역폭 기록) |
| `demo.py` | `1` 조각과 작업 그래프 · 일꾼 수별 끝나는 시각, `2` out/에 재생 목록 쓰기, `3` ABR 대 1080p 고정 |
| `solutions/resumable.py` | 연습 풀이: 조각으로 나눠 이어 올리기 대 처음부터 다시 |

```bash
python3 demo.py 1
python3 demo.py 2
python3 demo.py 3
python3 -m unittest
```

화질 사다리 값(640x360 365kbps · 1280x720 3,000kbps · 1920x1080 6,000kbps)은 Apple 「HLS Authoring Specification for Apple Devices」의 H.264 예시 줄이다.
변환 속도(영상 1초에 0.3 · 0.8 · 1.5초), ±20% 흔들림, 대역폭 기록, 80% 규칙은 설명을 위한 가정이다.

## 연습 문제
1GB 영상을 올리다 중간에 끊기는 경우를 흉내 내어, 처음부터 다시 올릴 때와 50MB 조각으로 나눠 끊긴 조각만 다시 올릴 때 보낸 양을 비교해 보세요. 풀이: `solutions/resumable.py`
