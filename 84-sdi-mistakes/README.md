# 면접 연습 대본 검사기 (파이썬 표준 라이브러리만)

연습한 답변을 시각과 함께 적은 대본(`transcripts/*.txt`)을 읽고, 면접에서 자주 하는 실수의 신호를 센다.
신호와 기준(요구 질문 3개 이상, 숫자 3개 이상, 트레이드오프 말 2번 이상, 장애 대비 1번 이상, 말 없는 틈 3분 이하, 깊게 파기 10분 이상)은
Meta Full Loop Interview Guide · ByteByteGo 「A framework for system design interviews」 · Hello Interview Delivery Framework의 조언을 연습용으로 옮긴 이 강의의 값이다. 공식 채점표가 아니다.

대본 형식: `[mm:ss] 나: …`, `[mm:ss] 면접관: …`, 걸음이 바뀌는 곳에 `[mm:ss] # 걸음 이름`.

| 파일 | 역할 |
|---|---|
| `checker.py` | `parse`, `check`(걸음별 분 · 신호 다섯), `RULES`, `flags` |
| `demo.py` | `1` 약한 판(`weak.txt`), `2` 고친 판(`better.txt`) |
| `solutions/my_answer.txt` | 연습 문제 풀이 예시 |

```bash
python3 demo.py 1
python3 demo.py 2
python3 -m unittest
```

## 연습 문제
앞 수업에서 푼 문제 하나(예: URL 단축기)를 45분 동안 소리 내어 풀고, 시각을 붙여 대본으로 적어 `python3 -c "from checker import *; print(flags(check(open('내대본.txt').read())))"`로 검사해 보세요. 풀이 예시: `solutions/my_answer.txt`
