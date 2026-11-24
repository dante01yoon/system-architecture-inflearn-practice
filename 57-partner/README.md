# partner — 외부 파트너 API 인증·인가 (파이썬 표준 라이브러리만, 강의용 장난감)

> 이 폴더의 보안 코드는 개념을 보여 주는 장난감입니다. 실서비스에서는 검증된 인가 서버·JWT 라이브러리·게이트웨이 기능을 쓰세요.

| 파일 | 역할 |
|---|---|
| `signing.py` | HMAC-SHA256 요청 서명(메서드 · 경로 · 시각 · nonce · 본문 해시), 5분 시각 창, nonce 캐시, 키 id별 비밀값(교체 중 둘 다 유효) |
| `tokens.py` | 클라이언트 크레덴셜 토큰 발급(scope · aud · exp)과 검사. 진짜 JWT가 아니다(헤더·alg 없음, HMAC 한 가지로 서버가 고정) |
| `demo.py` | `1` 서명: 통과 · 본문 변조 · 재전송 · 오래된 시각 · 틀린 비밀값, `2` 토큰: scope 403 · invalid_scope · 변조 · aud · 만료 · 비밀값 교체 |
| `solutions/rate_limit.py` | 연습 풀이(파트너별 1분 한도 → 429) |

```bash
python3 demo.py 1
python3 demo.py 2
python3 -m unittest
```
