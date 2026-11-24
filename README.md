# 실리콘밸리 개발자와 함께 공부하는 시스템 아키텍처 — 실습 자료

인프런 강의 「실리콘밸리 개발자와 함께 공부하는 시스템 아키텍처」의 수업별 예제 코드입니다.

- 강의: https://inf.run/QfEHe
- 파이썬 3.10 이상, 표준 라이브러리만 씁니다. 따로 설치할 것이 없습니다.
- 폴더 앞 번호 = 인프런 수업 번호. 각 폴더의 README에 실행 명령과 연습 문제가 있습니다.

```bash
git clone https://github.com/dante01yoon/system-architecture-inflearn-practice.git
cd system-architecture-inflearn-practice/15-cqrs
python3 demo.py
```


## 섹션 0. 시작하기

| 수업 | 제목 | 폴더 |
|---|---|---|
| 1 | 이 강의에서 배우는 것과 순서 | — |
| 2 | 뒤에서 계속 쓰는 말 세 가지 — 품질 요구사항, 트레이드오프, 결합도 | [02-terms](02-terms/) |

## 섹션 1. 아키텍처 스타일과 패턴

| 수업 | 제목 | 폴더 |
|---|---|---|
| 3 | 아키텍처 스타일 ① 모놀리식 계열 — 레이어드, 모듈러 모놀리스, 마이크로커널 | [03-styles-mono](03-styles-mono/) |
| 4 | 아키텍처 스타일 ② 분산 계열 한눈에 보기와 고르는 기준 | [04-styles-dist](04-styles-dist/) |
| 5 | 서비스를 얼마나 잘게 쪼갤까 — 아키텍처 퀀텀 | [05-quantum](05-quantum/) |
| 6 | MSA ① 무엇이고 왜 나왔나 — 독립 배포와 콘웨이 법칙 | [06-msa-why](06-msa-why/) |
| 7 | MSA ② 서비스 경계 정하기 — 바운디드 컨텍스트와 애그리거트 | [07-msa-bounds](07-msa-bounds/) |
| 8 | MSA ③ 서비스마다 자기 데이터 — Database per Service, 동기 대 비동기 | [08-msa-data](08-msa-data/) |
| 9 | MSA ④ 분산 모놀리스 함정과 쓰지 말아야 할 때 | [09-msa-trap](09-msa-trap/) |
| 10 | EDA ① 「이벤트」라는 말의 네 가지 뜻 | [10-eda-event](10-eda-event/) |
| 11 | EDA ② 브로커 대 미디에이터, Pub/Sub와 Dead Letter Channel | [11-eda-topo](11-eda-topo/) |
| 12 | EDA ③ 큐와 로그 — 전달 보장, 순서, 멱등 소비자 | [12-eda-log](12-eda-log/) |
| 13 | 패턴이란 — 문제와 트레이드오프의 짝 | [13-pattern](13-pattern/) |
| 14 | 패턴 지도 — 문제에서 출발해 패턴 찾기 | [14-patmap](14-patmap/) |
| 15 | CQRS — 쓰는 길과 읽는 길을 나누기 | [15-cqrs](15-cqrs/) |
| 16 | Saga ① 1987년 논문 — 긴 트랜잭션을 나누기 | [16-saga](16-saga/) |
| 17 | Saga ② 코레오그래피 대 오케스트레이션 | [17-saga2](17-saga2/) |
| 18 | API Gateway — 문 하나로 모으기 | [18-gateway](18-gateway/) |
| 19 | Circuit Breaker — 장애가 번지지 않게 끊기 | [19-breaker](19-breaker/) |
| 20 | Bulkhead·Timeout·재시도와 멱등성 | [20-resil](20-resil/) |
| 21 | 이벤트 소싱 — 바뀐 기록을 원본으로 | [21-evsrc](21-evsrc/) |
| 22 | Strangler Fig — 레거시를 조금씩 갈아 끼우기 | [22-strangler](22-strangler/) |
| 23 | 의존성 규칙 — 안쪽은 바깥을 모른다 | [23-deprule](23-deprule/) |
| 24 | 헥사고날 아키텍처 — 포트와 어댑터 | [24-hexa](24-hexa/) |
| 25 | 큐로 폭주 요청 받아 내기 | [25-loadlevel](25-loadlevel/) |
| 26 | 섹션 1 퀴즈 | — |

## 섹션 2. 문서화와 평가

| 수업 | 제목 | 폴더 |
|---|---|---|
| 27 | 얼마나 문서화할까 — 위험만큼만 설계한다 | [27-enough](27-enough/) |
| 28 | 4+1 뷰 모델 — 한 그림으로는 부족하다 | [28-fourplusone](28-fourplusone/) |
| 29 | C4 모델 — 지도처럼 확대해 가며 그리기 | [29-c4](29-c4/) |
| 30 | ADR — 결정과 이유를 남기기 | [30-adr](30-adr/) |
| 31 | arc42 템플릿 — 문서의 빈칸 채우기 | [31-arc42](31-arc42/) |
| 32 | ATAM — SEI 공식 평가법 | [32-atam](32-atam/) |
| 33 | 가벼운 아키텍처 리뷰 체크리스트 | [33-review](33-review/) |
| 34 | 피트니스 함수 — 아키텍처 규칙을 자동 검사로 | [34-fitness](34-fitness/) |
| 35 | 섹션 2 퀴즈 | — |

## 섹션 3. 실전 설계 훈련

| 수업 | 제목 | 폴더 |
|---|---|---|
| 36 | 트래픽이 몰릴 때 제일 먼저 할 일 | [36-traffic](36-traffic/) |
| 37 | 분산의 세 가지 기준 | [37-distrib](37-distrib/) |
| 38 | 데이터 시스템 아키텍처의 트레이드오프 | [38-ddia-tradeoff](38-ddia-tradeoff/) |
| 39 | 비기능 요구사항 정의하기 — 성능을 숫자로, p99 | [39-nfr](39-nfr/) |
| 40 | 데이터 모델 — 관계형·문서·그래프 | [40-ddia-model](40-ddia-model/) |
| 41 | 저장소 엔진 — B-tree 대 LSM-tree, OLTP 대 OLAP | [41-ddia-storage](41-ddia-storage/) |
| 42 | 인코딩과 스키마 진화 — 하위·상위 호환 | [42-ddia-encoding](42-ddia-encoding/) |
| 43 | 복제 — 리더-팔로워와 복제 지연 | [43-ddia-replication](43-ddia-replication/) |
| 44 | 샤딩 — 키 범위 대 해시, 핫스팟, 재균형 | [44-ddia-sharding](44-ddia-sharding/) |
| 45 | 트랜잭션과 격리 수준 — 더티 리드부터 write skew까지 | [45-ddia-txn](45-ddia-txn/) |
| 46 | 분산 시스템에서 믿을 수 없는 것들 — 네트워크, 시계, 멈춤 | [46-ddia-trouble](46-ddia-trouble/) |
| 47 | 일관성과 합의 — 선형성, CAP, 2PC | [47-ddia-consensus](47-ddia-consensus/) |
| 48 | 배치 처리 — 한꺼번에 모아서 계산하기 | [48-ddia-batch](48-ddia-batch/) |
| 49 | 스트림 처리와 CDC — 로그로 흐르는 데이터 | [49-ddia-stream](49-ddia-stream/) |
| 50 | 스트리밍 시스템의 철학 — 파생 데이터 | [50-ddia-philo](50-ddia-philo/) |
| 51 | 올바른 일 하기 — 데이터 윤리와 개인정보 | [51-ddia-ethics](51-ddia-ethics/) |
| 52 | 횡단 관심사를 코드 수준에서 처리하기 | [52-crosscut](52-crosscut/) |
| 53 | 요구에서 설계까지 — 선착순 예약 시스템 | [53-booking](53-booking/) |
| 54 | 좌석 선점과 만료 — 중복 판매 막기 | [54-seat](54-seat/) |
| 55 | 결제는 됐는데 주문이 안 끝났다 — 정합성과 복구 | [55-payment](55-payment/) |
| 56 | Transactional Outbox — 저장과 발행을 함께 | [56-outbox](56-outbox/) |
| 57 | 외부 파트너 API 인증·인가 | [57-partner](57-partner/) |
| 58 | 실제 사례 분석 — 공개 장애 보고서 읽기 | [58-case](58-case/) |
| 59 | Redis는 왜 싱글 스레드인가 | [59-redis-like](59-redis-like/) |
| 60 | Kafka는 왜 이렇게 설계됐나 | [60-kafka-like](60-kafka-like/) |
| 61 | 섹션 3 퀴즈 | — |

## 섹션 4. 운영을 고려한 아키텍처 설계

| 수업 | 제목 | 폴더 |
|---|---|---|
| 62 | SLI·SLO·Error Budget — 얼마나 믿을 만해야 하나 | [62-slo](62-slo/) |
| 63 | 모니터링 ① Four Golden Signals | [63-golden](63-golden/) |
| 64 | 모니터링 ② USE와 RED | [64-usered](64-usered/) |
| 65 | 모니터링 ③ 셋을 비교하고 고르기 | [65-monitor-compare](65-monitor-compare/) |
| 66 | 무중단 배포 — 서비스와 DB를 안전하게 바꾸기 | [66-deploy](66-deploy/) |
| 67 | 섹션 4 퀴즈 | — |

## 섹션 5. 시스템 디자인 면접

| 수업 | 제목 | 폴더 |
|---|---|---|
| 68 | 시스템 디자인 면접은 무엇을 보나 | [68-sdi-what](68-sdi-what/) |
| 69 | 답변 틀 — 요구에서 깊게 파기까지 | [69-sdi-frame](69-sdi-frame/) |
| 70 | 규모 어림셈 — QPS, 저장 용량, 대역폭 | [70-estimate](70-estimate/) |
| 71 | 서버 한 대에서 백만 명까지 | [71-scale](71-scale/) |
| 72 | 데이터베이스 고르기 — SQL 대 NoSQL | [72-sdi-db](72-sdi-db/) |
| 73 | 캐시와 CDN — 캐시 전략과 만료 | [73-sdi-cache](73-sdi-cache/) |
| 74 | API와 통신 방식 — REST, gRPC, WebSocket, 메시지 큐 | [74-sdi-api](74-sdi-api/) |
| 75 | Consistent Hashing | [75-sdi-chash](75-sdi-chash/) |
| 76 | URL 단축기 — 고유 ID 만들기 | [76-sdi-url](76-sdi-url/) |
| 77 | Rate Limiter | [77-sdi-ratelimit](77-sdi-ratelimit/) |
| 78 | 알림 시스템 | [78-sdi-notify](78-sdi-notify/) |
| 79 | 뉴스 피드 — fan-out | [79-sdi-feed](79-sdi-feed/) |
| 80 | 채팅 시스템 | [80-sdi-chat](80-sdi-chat/) |
| 81 | 영상 스트리밍 — YouTube 설계 | [81-sdi-video](81-sdi-video/) |
| 82 | 위치 기반 호출 — Uber 설계 | [82-sdi-uber](82-sdi-uber/) |
| 83 | Key-Value 저장소 | [83-sdi-kv](83-sdi-kv/) |
| 84 | 면접에서 자주 하는 실수 | [84-sdi-mistakes](84-sdi-mistakes/) |
| 85 | 모의 면접 한 판 — 처음부터 끝까지 | [85-sdi-mock](85-sdi-mock/) |
| 86 | 섹션 5 퀴즈 | — |
