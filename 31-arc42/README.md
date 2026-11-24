# arc42 — 문서의 빈칸 채우기

`arc42.py`: arc42 열두 장(소개와 목표 … 용어집) 마크다운 뼈대를 만들고(`skeleton`), 채운 문서를 `## N.` 제목으로 나눠 장마다 채움·짧음·빈칸을 매기고(`check`), 9장에 링크된 ADR 파일이 `adr/` 폴더에 있는지, 폴더의 ADR 중 9장에서 빠진 것이 있는지 알려 준다. 짧음 = `TODO`가 있거나 주석을 뺀 본문이 40자 미만. 표준 라이브러리만 쓴다.

`bookshop/arc42.md`는 반쯤 채운 서점 문서, `bookshop/adr/`는 ADR 세 개(0001·0002·0003)다. 9장은 없는 0004를 가리키고 0003을 빠뜨렸다.

    python3 demo.py                          # skeleton.md를 만들고 서점 문서를 검사
    python3 -m unittest
    python3 solutions/scenario_measure.py    # 연습 문제 풀이: 10장에서 측정 칸이 빈 시나리오 찾기

장 이름은 docs.arc42.org(2026-11-14 확인)의 열두 장을 우리말로 옮긴 것이다.
