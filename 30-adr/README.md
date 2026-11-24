# ADR 수업 예제: 결정과 이유를 파일로 남기기 (파이썬 표준 라이브러리만)

Michael Nygard, 「Documenting Architecture Decisions」(2011-11-15)의 양식(제목 · 상태 · 맥락 · 결정 · 결과)으로
`doc/arch/adr-NNN.md` 파일을 만드는 작은 도구.

| 파일 | 역할 |
|---|---|
| `adr.py` | `new "<제목>"` 번호 붙은 새 결정 · `accept <번호>` 승인 · `supersede <번호> "<제목>"` 새 결정으로 대체(서로 링크, 옛 파일은 상태 칸만 바뀜) · `list` |
| `demo.py` | 임시 폴더에서 서점 결정 세 개를 만들고 2번을 3번으로 대체. `python3 demo.py show`는 대체된 2번 파일 전체 |
| `solutions/deprecate.py` | 연습 문제 풀이 |

```bash
python3 demo.py
python3 demo.py show
python3 adr.py new "주문 DB는 PostgreSQL을 쓴다"   # 지금 폴더의 doc/arch/에 만든다
python3 -m unittest
```

## 연습 문제

대신할 결정 없이 그만 쓰게 된 결정은 어떻게 남길까요? `adr.py`에 `deprecate <번호> "<이유>"`를 붙여 상태를 「폐기됨」으로 바꾸세요. 맥락·결정·결과는 건드리지 않습니다.
풀이: `python3 solutions/deprecate.py`
