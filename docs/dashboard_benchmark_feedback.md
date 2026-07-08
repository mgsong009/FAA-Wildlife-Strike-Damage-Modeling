# Dashboard Benchmark Feedback

작성일: 2026-07-02

## 목적

이 대시보드는 발표 자료가 아니라 FAA wildlife strike damage modeling 결과를 항공 시스템에 적용하면 어떤 방식으로 보일 수 있는지 보여주는 시연물이다. 핵심은 “야생동물 충돌 발생 예측”이 아니라, 이미 보고된 wildlife strike incident 이후 항공기 손상 가능성과 검토 우선순위를 설명하는 것이다.

벤치마킹 기준은 Tableau/Power BI형 분석 대시보드, 항공 운항 콘솔, post-strike review workflow, 모델 해석 화면이다. 모든 화면은 `reported incidents`, `post-strike review`, `inspection priority support`, `not live operations`, `not airline safety ranking` 경계를 유지해야 한다.

## 최종 구성

1. Analytics Overview
   - Tableau/Power BI처럼 KPI, 필터, 월별 추세, 조건별 손상률, 모델 성능, key reads를 한 화면에서 보여준다.
   - Phase, Altitude, Wildlife Size 필터가 실제 KPI와 차트를 갱신한다.

2. Damage Assessment
   - 개별 보고 사례를 선택하고 damage review score, inspection priority recommendation, 조건별 근거를 확인한다.
   - 점수는 최종 정비 판단이 아니라 historical condition rates 기반의 dashboard review score임을 명시한다.

3. Flight Phase Explorer
   - Take-off Run, Climb, Descent, Approach, Landing Roll, Taxi 흐름으로 비행 단계별 손상률 차이를 보여준다.
   - 실시간 항공기 추적이 아니라 historical phase profile임을 명시한다.

4. Risk Factor Intelligence
   - 손상률 bar chart뿐 아니라 frequency vs severity matrix를 추가했다.
   - 많이 보고되는 조건과 손상률이 높은 조건이 다를 수 있음을 한 화면에서 설명한다.

5. Operator Application Demo
   - Southwest Airlines를 “highest reported operator” 데모 기준으로 사용한다.
   - review queue, airport layout, selected report detail을 연결해 항공 시스템 적용 예시처럼 보이도록 구성했다.
   - 항공사 안전 순위나 운영 노출 위험 추정으로 보이지 않도록 문구를 유지한다.

## 스크린샷 검수

새 스크린샷은 다음 경로에 저장했다.

- `docs/dashboard_screenshots/00_analytics_overview.png`
- `docs/dashboard_screenshots/01_damage_assessment.png`
- `docs/dashboard_screenshots/02_flight_phase_explorer.png`
- `docs/dashboard_screenshots/03_risk_factor_intelligence.png`
- `docs/dashboard_screenshots/04_operator_application_demo.png`

브라우저 캡쳐 기준으로 `NaN`, `undefined` 텍스트는 발견되지 않았다. 3번과 4번 화면은 수정 후 재캡쳐했다.

## 화면별 판단

### 0. Analytics Overview

의도 달성도: 높음

Tableau/Power BI형 분석 화면에 가장 가깝다. 필터가 실제로 작동하고, KPI와 조건별 차트가 갱신되어 “분석 대시보드”라는 인상이 생겼다. 모델 성능과 key reads도 함께 보여 비전공 교수가 전체 결과를 빠르게 파악하기 좋다.

주의점:
- 화면이 의도적으로 복잡하므로 발표 중 이 화면을 오래 설명하기보다 “전체 분석 출처 화면”으로 짧게 보여주는 편이 좋다.
- 데이터가 reported incidents 기준이라는 점을 말로도 한 번 더 짚어야 한다.

### 1. Damage Assessment

의도 달성도: 높음

개별 사례 선택, score, recommendation, evidence 구조가 명확하다. 이번 수정으로 score basis가 추가되어 실제 정비 확률이나 최종 판단으로 오해될 위험이 줄었다.

주의점:
- 현재 점수는 dashboard demonstration score이므로, 최종 모델 pickle을 직접 호출한 실시간 예측처럼 말하면 안 된다.
- “inspection priority support”로 설명해야 한다.

### 2. Flight Phase Explorer

의도 달성도: 높음

비행 단계 흐름이 항공 교수에게 가장 직관적으로 보일 가능성이 크다. Take-off Run에서 Taxi까지 흐름이 보이고, 각 단계별 손상률이 바로 읽힌다.

주의점:
- 실시간 flight tracking 화면처럼 보이지 않도록 `not live tracking` 문구를 유지해야 한다.

### 3. Risk Factor Intelligence

의도 달성도: 중상에서 높음

frequency vs severity matrix가 추가되면서 단순 bar chart 화면에서 벤치마킹한 safety intelligence 화면에 가까워졌다. 손상률이 높은 조건과 보고 수가 많은 조건을 분리해 보여주는 점이 좋다.

이번 검수에서 고친 점:
- 상위 라벨이 버블 위에서 겹치던 문제를 우측 고정 라벨 영역으로 이동해 읽기 좋게 했다.

주의점:
- matrix는 demo 목적의 해석 시각화다. 통계적 인과관계나 실제 위험 노출량으로 해석하지 않게 말해야 한다.

### 4. Operator Application Demo

의도 달성도: 중상

이전보다 운항 검토 콘솔에 가까워졌다. Review queue가 dense table처럼 바뀌었고, airport layout에 runway, taxiway, terminal, wildlife zone, corridor label이 들어가 항공 시스템 적용 예시로 이해하기 쉬워졌다.

이번 검수에서 고친 점:
- queue score 열이 좁아 잘려 보이던 문제를 수정했다.
- 선택 report callout이 지도와 우측 상세 패널을 연결한다.

주의점:
- 공항 레이아웃은 실제 공항 지도가 아니라 scenario layout이다. 실제 ATC/airport ops 시스템으로 과장하지 말아야 한다.
- Southwest는 highest reported operator demo일 뿐 안전 순위가 아니다.

## 종합 평가

현재 결과물은 “모델 결과를 항공 시스템에 도입하면 어떤 식으로 보여줄 수 있는가”라는 원래 목적에 꽤 잘 맞는다. 특히 항공 교수 입장에서는 Flight Phase Explorer와 Operator Application Demo가 직관적이고, Analytics Overview가 분석 신뢰도를 보조한다.

다만 모든 화면은 실제 운영 시스템이 아니라 reported incident 기반 의사결정 지원 데모라는 경계를 유지해야 한다. 이 경계만 발표에서 명확히 잡으면, 모델 결과가 단순 표나 성능 지표가 아니라 실제 post-strike review workflow에 들어갈 수 있다는 인상을 줄 수 있다.
