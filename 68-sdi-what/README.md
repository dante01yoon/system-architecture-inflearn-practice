# 시스템 디자인 면접 자기 채점표 (파이썬 표준 라이브러리만)

연습 면접을 한 판 끝낸 뒤, 네 영역(문제 탐색 · 해법 설계 · 기술 깊이 · 기술 소통) × 세 문항에 예(y)/아니요(n)로 답하면 영역마다 점수와 다음에 고칠 점 하나를 알려 준다.
네 영역 이름은 Meta 「Software Engineer Full Loop Interview Guide」의 디자인 면접 네 focus area를 따랐고, 문항은 그 설명을 연습용으로 풀어 쓴 것이다(공식 채점표가 아니다).

| 파일 | 역할 |
|---|---|
| `rubric.py` | `RUBRIC`(영역·문항·조언), `parse`(y/n 12개), `score`, `weakest` |
| `sessions.py` | 예시 연습 두 판(약한 판 · 강한 판) |
| `demo.py` | `1` 약한 판 채점, `2` 강한 판 채점 |
| `solutions/my_session.py` | 연습 문제 풀이: 내 답으로 채점 |

```bash
python3 demo.py 1
python3 demo.py 2
python3 -m unittest
python3 solutions/my_session.py "y y n  y n y  n y n  y y n"
```

## 연습 문제
URL 단축기를 45분 동안 혼자 소리 내어 풀어 보고(녹음해 두면 좋다), 끝난 뒤 열두 문항에 답해 채점해 보세요. 가장 약한 영역 하나만 골라 다음 판에서 고칩니다.
