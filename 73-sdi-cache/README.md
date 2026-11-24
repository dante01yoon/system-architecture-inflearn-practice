# 캐시와 요청 몰림 (파이썬 표준 라이브러리만)

`OrderedDict`로 만든 LRU 캐시(TTL 포함)로 캐시 크기와 적중률의 관계를 재고, 인기 키가 만료되는 순간 요청 100개가 원본에 몰리는 모습(cache stampede)과
키마다 자물쇠 하나로 막는 single-flight, TTL 흔들기(jitter)를 실행해 본다. 캐시 1ms · DB 20ms는 설명을 위한 가정이다.

| 파일 | 역할 |
|---|---|
| `cache.py` | `LRU`, `zipf_keys`, `Origin`(느린 원본), `read`(cache-aside), `read_once`(single-flight), `jitter_ttl`, `early`(확률적 조기 만료, Vattani 외 2015) |
| `demo.py` | `1` 캐시 크기와 적중률, `2` 만료 순간 요청 100개, `3` TTL 흔들기 |
| `solutions/lfu.py` | 연습 문제 풀이: LFU와 LRU 비교 |

```bash
python3 demo.py 1
python3 demo.py 2
python3 demo.py 3
python3 -m unittest
```

## 연습 문제
가장 적게 쓴 키부터 내보내는 LFU 캐시를 만들어 `demo.py 1`과 같은 요청 줄에서 LRU와 적중률을 비교해 보세요. 풀이: `solutions/lfu.py`
