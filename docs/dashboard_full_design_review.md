# Dashboard Full Design Review

검토 기준: 2026-07-02 최신 캡쳐본 `docs/dashboard_screenshots` 5개 화면. 목표는 발표자료가 아니라, FAA wildlife strike reported incident damage model이 실제 항공 업무 시스템에 들어갔을 때 어떻게 보이는지 설득하는 대시보드다.

## 공통 판단

- 전체 톤: 어두운 airport operations console 스타일은 유지되고 있으며, 페이지 전환 시 색감과 UI 밀도는 일관적이다.
- 데이터 경계: 화면 대부분이 reported incidents, post-strike review, decision-support demo로 명시되어 있어 실시간 항공 관제나 항공사 안전 순위로 오해될 위험은 줄었다.
- 남은 핵심 문제: 일부 페이지가 수치와 그림은 있으나 “이 결과를 실제 업무에서 어떻게 읽는가”가 부족했다. 그래서 이번 수정은 새 기능 추가보다 운영 해석, handoff, boundary를 보강하는 방향으로 진행했다.

## 0. Analytics Overview

### 의도

Tableau/Power BI 스타일의 복합 분석 대시보드. 데이터에서 어떤 결과가 도출되었고, 이후 시스템 페이지의 근거가 무엇인지 한 번에 보여준다.

### 캡쳐 기준 장점

- KPI, 월별 추세, class balance, model comparison, feature importance, species damage rate가 한 화면에 조밀하게 배치되어 BI 분석 화면의 인상이 난다.
- 필터가 Phase, Altitude, Distance, Wildlife, Number struck, Aircraft mass, Sky condition까지 확장되어 “조건이 많은데 왜 일부만 보나?”라는 의문은 많이 줄었다.
- 손상 사례가 rare class임을 confusion matrix summary에서 설명하고 있어 단순 accuracy 중심 해석을 피한다.

### 캡쳐 기준 문제

- 필터가 많아진 만큼 현재 어떤 조건 lens로 보고 있는지 한눈에 보이지 않았다.
- Model comparison에서 Random Forest F1이 Decision Tree보다 조금 높아 보이는데, 최종 모델이 Decision Tree인 이유가 화면 안에서 설명되지 않았다. 비전공 교수 입장에서는 “왜 더 높은 모델을 안 썼지?”라고 볼 수 있다.
- 월별 chart는 분석 화면으로는 충분하지만, 축/맥락 설명이 아주 친절하지는 않다.

### 이번 수정

- 필터 패널 하단에 Current lens 영역을 추가해 active filter 수와 선택 조건을 보여주도록 했다.
- Model comparison 아래 Selection note를 추가해 Decision Tree를 demo model로 둔 이유가 해석 가능성과 inspection-support workflow 설명성 때문임을 밝혔다.

## 1. Post-Strike Damage Assessment

### 의도

보고된 충돌 사건 하나가 들어왔을 때 점검 우선순위를 올릴지 판단하는 핵심 사용 화면.

### 캡쳐 기준 장점

- “Should this reported strike be elevated for inspection review?”라는 질문형 제목은 화면 목적이 명확하다.
- Score, risk badge, condition evidence, review boundary가 있어 점수의 근거와 한계를 동시에 보여준다.
- 정비 승인이나 실시간 원인 진단이 아니라 review attention ranking임을 명시한다.

### 캡쳐 기준 문제

- 중앙 패널 하단에 여백이 남아 결과가 다음 업무로 어떻게 넘어가는지 약했다.
- 선택 사례의 조건은 보이지만 실제 운영자가 어떤 action을 취해야 하는지가 조금 덜 보였다.
- 우측 boundary와 중앙 evidence가 잘 되어 있어도, “그래서 다음에 뭘 하나?”가 빠지면 시스템 도입 화면으로는 힘이 약해진다.

### 이번 수정

- 중앙 하단에 Review action 영역을 추가했다.
- “Queue for maintenance review package”와 3단계 checklist를 넣어, 점수 산출 이후 reported phase/altitude 확인, wildlife/species 확인, priority inspection review routing으로 이어지는 흐름을 보여주도록 했다.

## 2. Flight Phase Risk Explorer

### 의도

비행 단계에 따라 보고된 손상률이 어떻게 달라지는지 항공 교수님이 직관적으로 이해하게 만드는 화면.

### 캡쳐 기준 장점

- 비행 궤적형 프로파일은 Take-off, Climb, Descent, Approach, Landing Roll, Taxi 흐름을 직관적으로 보여준다.
- 우측 selected phase readout에 damage rate, risk lift, reports, sequence가 있어 선택 단계의 수치를 빠르게 읽을 수 있다.
- 하단 phase, altitude, distance 차트가 항공 맥락을 보완한다.

### 캡쳐 기준 문제

- 우측 selected phase 패널이 수치 이후 비어 보이며, 사용자가 이 수치를 어떻게 해석해야 하는지 약했다.
- “not live tracking”은 표시되어 있지만, 선택 phase를 실제 업무 질문과 연결하는 문장이 부족했다.
- 큰 궤적 그림은 좋지만 데이터 해석 패널이 짧으면 장식적 요소로 보일 위험이 있다.

### 이번 수정

- 우측 패널에 phase context 영역을 추가했다.
- Operational question, How to use, Boundary를 넣어 이 화면이 phase별 review attention 비교용이며 live hazard display가 아님을 명확히 했다.

## 3. Wildlife & Aircraft Risk Factors

### 의도

모델이 어떤 조건을 손상 위험 요인으로 보는지 설명하고, 모델 해석과 항공 안전 인사이트를 연결하는 화면.

### 캡쳐 기준 장점

- Frequency vs severity matrix는 보고 건수와 손상률이 다르게 움직인다는 메시지를 잘 전달한다.
- Wildlife size, altitude, distance, species, feature importance를 한 화면에서 비교할 수 있다.
- 좌측 상단 driver cards와 interpretation stack은 모델 결과를 설명하는 데 도움이 된다.

### 캡쳐 기준 문제

- 좌측 상단 패널이 우측 matrix보다 짧아 아래쪽에 큰 공백이 생겼고, 미완성처럼 보일 수 있었다.
- “위험 요인”이라는 표현이 wildlife occurrence probability나 공항/항공사 안전성 평가로 오해될 수 있어 guardrail이 더 필요했다.
- matrix 라벨의 구분 문자가 일부 환경에서 깨져 보일 가능성이 있어 전문 화면 품질을 낮출 수 있었다.

### 이번 수정

- interpretation stack에 Operational use를 추가했다.
- Best read / Do not read as guardrail을 추가해 이 화면이 reported strike 이후 damage severity 해석용이지 발생 확률이나 safety ranking이 아님을 강조했다.
- 라벨 구분은 안전한 ASCII slash 형식으로 유지하도록 정리했다.

## 4. Operator / Airport Application Demo

### 의도

가장 높은 reported operator 예시를 기준으로, 모델 결과가 항공사/공항 시스템 화면에 들어갔을 때의 적용 가능성을 보여주는 데모.

### 캡쳐 기준 장점

- 좌측 queue, 중앙 surface scenario layer, 우측 selected report 구조는 airport operations console에 가깝다.
- 지도에는 runway, taxiway, terminal apron, wildlife review zone, approach corridor, reported cluster band가 있어 이전보다 항공 화면으로 읽힌다.
- “highest reported operator example”과 safety ranking 아님을 명시해 오해를 줄인다.

### 캡쳐 기준 문제

- 중앙 지도 아래 readout은 보강되었지만, 우측 selected report 패널은 아직 상세 정보 나열 성격이 강했다.
- 선택된 case가 review package로 넘어가는 업무 handoff가 더 직접적으로 보여야 실제 도입 시스템처럼 느껴진다.
- 공항 도식은 여전히 stylized scenario map이며, 실제 GIS/공항 도면급 현실성까지는 아니다.

### 이번 수정

- 우측 selected report 패널에 Decision-support handoff 영역을 추가했다.
- airport/phase 확인, queue score 비교, inspection review package 전달이라는 3단계 운영 흐름을 명시했다.

## 종합 평가

수정 전 대시보드는 시각적 틀은 갖췄지만, 일부 화면에서 “좋아 보이는 수치와 그림”이 “실제 항공 업무 의사결정 흐름”으로 완전히 이어지지 않았다. 이번 수정의 핵심은 모든 페이지에 같은 시스템 메시지를 심는 것이다.

> reported incident data → damage risk evidence → review priority → operational handoff

현재 상태는 발표자료와 별개로 보여줄 수 있는 결과 대시보드로 충분히 설득력이 있다. 다음 단계에서 더 높일 수 있는 지점은 4번의 surface map을 실제 공항 도면/운영 지도에 더 가까운 시각 언어로 고도화하는 것이다.

## Focused Re-Review: 3번 Frequency vs Severity / 4번 Surface Scenario Layer

사용자 피드백에 따라 3페이지 전체가 아니라 `Frequency vs severity` 영역, 4페이지 전체가 아니라 `Surface scenario layer` 영역만 다시 검토했다.

### 3번 Frequency vs Severity 판단

이전 상태는 버블 수, 라벨 수, 사분면 문구, 하단 요약 칩이 동시에 경쟁했다. 분석가는 의미를 해석할 수 있지만, 비전공 항공 교수님이 5초 안에 보기에 “어떤 조건이 핵심인가”보다 “점이 많다”가 먼저 보이는 문제가 있었다. 특히 상위 species 라벨 4개와 전체 조건 버블이 겹쳐 matrix가 설명 도구가 아니라 복잡한 산점도처럼 읽혔다.

수정 방향은 모든 조건을 한 번에 보여주는 것이 아니라, 대표 high-severity 조건과 high-volume 조건만 남겨 matrix의 목적을 명확히 하는 것이다. 따라서 matrix에 표시되는 점을 상위 손상률 조건과 고빈도 조건으로 제한하고, 라벨은 상위 3개만 유지했다. 사분면 문구도 긴 설명 대신 `higher severity`, `higher volume`으로 줄였다.

### 4번 Surface Scenario Layer 판단

이전 상태는 runway, taxiway, terminal, wildlife zones, approach/departure curves, density band, cluster band, 24개 incident marker, selected trail, callout이 동시에 존재했다. 그 결과 실제 운영 지도라기보다 여러 시각 레이어를 얹은 데모 그림처럼 보였다. 특히 지도 안의 곡선과 원형 zone, 색상 band가 서로 겹쳐 정보 우선순위가 흐려졌다.

수정 방향은 runway 중심의 surface review layer로 단순화하는 것이다. 접근 corridor는 최소한의 dashed line으로 남기고, density band/departure path/cluster band를 제거했다. incident marker는 24개에서 10개로 줄였고, wildlife review zone도 2개만 남겼다. selected callout은 곡선 trail 대신 짧은 직선 연결로 바꾸어 지도 위 장식감을 줄였다.

### Follow-up Tightening

추가 검토에서 3번 matrix의 red severity 버블이 아직 많아 핵심 3개보다 red cluster가 먼저 보이는 문제가 남아 있었다. 따라서 matrix 표시 대상을 상위 severity 3개와 high-volume 대표 조건 4개로 더 줄이고, 버블 반경도 낮췄다. 4번 surface layer는 selected callout 박스와 선이 지도 위에서 다소 크게 느껴져, 중복 선을 제거하고 박스 크기를 줄였다.
