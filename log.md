# Change Log

완료된 수정 사항을 시간순으로 기록한다. 각 항목은 먼저 `todo.md`에 핵심 실행 문구를 작성한 뒤, 실제 반영과 검증이 끝나면 이곳으로 옮긴다.

## 2026-07-02

- Analytics Overview를 실제 BI형 분석 화면에 가깝게 강화했다.
  - 반영 결과: Phase, Altitude, Wildlife Size 필터를 추가하고, 선택 조건에 따라 KPI, 월별 추세, phase/size/altitude 차트가 연동되도록 변경했다. 최종 모델, threshold, precision, recall, F1을 보여주는 model validation 영역도 추가했다. `npm run build` 통과.

- Flight Phase Explorer의 비행 프로파일 흐름을 항공 맥락에 맞게 보정했다.
  - 반영 결과: 프로파일 다이어그램과 phase 선택 버튼을 Take-off Run, Climb, Descent, Approach, Landing Roll, Taxi 순서로 재정리했다. Phase ranking bar chart의 색상도 위험 기준 정렬을 유지했다. `npm run build` 통과.

- Risk Factor Intelligence에 frequency vs severity matrix를 추가했다.
  - 반영 결과: Size, Altitude, Distance, Number struck, Species 조건을 하나의 2축 matrix로 통합했다. X축은 보고 건수, Y축은 손상률, 버블 크기는 risk lift로 표현하고, 상위 위험 조건은 라벨과 요약 칩으로 강조했다. `npm run build` 통과.

- Operator Application Demo를 실제 항공 검토 콘솔처럼 보이게 조정했다.
  - 반영 결과: Review queue를 ID/Airport/Phase/Score 중심의 dense table로 재구성했고, 공항 SVG에는 runway, taxiway, terminal, wildlife zone, approach corridor, departure corridor, 선택 리포트 callout을 추가했다. `npm run build` 통과.

- Damage Assessment에서 점수의 의미와 한계를 명확히 보강했다.
  - 반영 결과: 중앙 결과 영역에 Score basis 블록을 추가해 historical condition rates 기반 dashboard review score임을 명시했다. 우측 evidence 패널에는 각 막대가 선택 조건의 과거 손상률이지 실시간 원인 진단이 아니라는 note를 추가했다. `npm run build` 통과.

- 스크린샷 검토에서 발견한 시각 문제를 수정했다.
  - 반영 결과: Risk matrix의 상위 라벨을 우측 고정 라벨 영역으로 재배치했고, Operator queue의 score 컬럼 폭을 재조정했다. 3번과 4번 화면을 재캡쳐해 개선을 확인했다. `npm run build` 통과.

- 최종 스크린샷 검토 결과를 바탕으로 `docs/dashboard_benchmark_feedback.md`를 읽을 수 있는 한국어 문서로 정리했다.
  - 반영 결과: 기존 인코딩이 깨져 보이던 피드백 문서를 최종 구성, 스크린샷 검토, 화면별 판단, 종합 평가 형식으로 다시 작성했다.

- 실제 Tableau/Power BI 분석 대시보드, airport operations console, aviation decision-support 화면의 벤치마킹 기준으로 대시보드 정보 구조와 시각 언어를 재정리했다.
  - 반영 결과: 0번 Analytics Overview의 상단 KPI를 Total Reports, Damaged Cases, Overall Damage Rate, Final Model, Threshold로 재구성하고 Precision/Recall/F1과 Confusion matrix summary를 별도 영역으로 이동했다. 3번의 빈 hero를 Wildlife & Aircraft risk driver briefing으로 교체했으며, 4번의 Operator / Airport Demo 용어와 queue ID, 경계 문구를 정리했다. `npm run build` 통과, 0/3/4번 화면 재캡쳐 및 `NaN`, `undefined`, 깨진 구분 문자 없음 확인.

- Post-Strike Assessment 화면을 캡쳐본 기준 전문가 피드백에 따라 재구성했다.
  - 반영 결과: 이전 화면은 “Inspection queue priority” 문구가 큰 빈 공간에 떠 있어 무엇을 판단하는 화면인지 약했으므로, 중앙 패널 상단을 “Should this reported strike be elevated for inspection review?” 질문으로 바꾸고 Selected report/Phase/Altitude/Wildlife 요약 strip을 추가했다. 게이지 옆에는 Elevate for inspection review와 Priority inspection recommended를 배치했고, 하단에는 Wildlife size, Flight phase, Altitude band, Airport distance 근거 타일을 추가했다. 우측 패널은 Review boundary로 바꿔 이 화면이 정비 승인이나 실시간 원인 진단이 아니라 reported case review ranking임을 명확히 했다. `npm run build` 통과, 1번 화면 재캡쳐 및 `NaN`, `undefined`, 기존 floating phrase 없음 확인.

- 0/2/3/4 페이지를 캡쳐본 기준 전문가 피드백에 따라 보정했다.
  - 반영 결과: 0번 Analytics는 조건 필터가 부족해 보이지 않도록 Phase, Altitude, Airport distance, Wildlife size, Number struck, Aircraft mass, Sky condition까지 확장했다. 2번 Flight Phase는 selected phase readout과 operational status를 추가하고, 비행 궤적에 altitude band와 surface label을 넣어 흐름을 명확히 했다. 3번 Risk Factors는 좌측 상단 아래 공백을 Severity/Frequency/Model read 해석 패널로 채웠다. 4번 Operator/Airport Demo는 surface map에 runway direction, review zones, density band, selected incident trail을 추가했다. `npm run build` 통과, 0/2/3/4 화면 재캡쳐 및 `NaN`, `undefined`, 깨진 문자 없음 확인.

- 4번 Operator/Airport Demo의 중앙 지도 아래 공백을 운영 readout으로 보강했다.
  - 반영 결과: 지도 아래에 Workflow handoff, Selected context, Surface layer use 영역을 추가해 “보고 사건이 공항 검토 큐로 들어오고, 모델 점수는 정비/엔지니어링 판단 전 triage layer로 쓰인다”는 흐름을 화면에서 바로 읽을 수 있게 했다. 4번 화면을 재캡쳐해 하단 공백이 미완성처럼 보이지 않는지 확인했고, `npm run build` 통과 및 `NaN`, `undefined`, 깨진 문자 없음 확인.

- 전체 5개 페이지를 최신 캡쳐본 기준으로 다시 전문가 검토하고 남은 완성도 문제를 보정했다.
  - 반영 결과: `docs/dashboard_full_design_review.md`를 작성해 0번부터 4번까지 의도, 캡쳐 기준 장점, 문제, 수정 방향, 반영 내용을 모두 정리했다. 0번 Analytics에는 Current lens와 Decision Tree 선택 이유를 추가했고, 1번 Assessment에는 Review action checklist를 추가했다. 2번 Flight Phase에는 Operational question/How to use/Boundary를 넣어 우측 패널의 빈 느낌을 줄였고, 3번 Risk Factors에는 Operational use와 Best read/Do not read as guardrail을 추가했다. 4번 Operator Demo에는 Decision-support handoff를 추가했다. `npm run build` 통과, 전체 5개 화면 재캡쳐 및 `NaN`, `undefined`, 깨진 문자 없음 확인.

- 사용자 지적에 따라 3페이지의 Frequency vs severity와 4페이지의 Surface scenario layer만 다시 집중 보정했다.
  - 반영 결과: 3번 Frequency vs severity는 전체 조건 버블을 모두 표시하던 방식이 난잡했으므로, 상위 손상률 조건과 고빈도 대표 조건만 matrix에 표시하도록 줄였다. 라벨은 상위 3개로 제한하고, 사분면 문구는 `higher severity`, `higher volume`으로 압축했으며, 요약 칩도 3개로 정리했다. 4번 Surface scenario layer는 density band, departure path, cluster band, 과도한 incident marker를 제거하고, runway, approach corridor, taxiway, terminal, wildlife review zone 2개 중심의 clean surface review layer로 재구성했다. incident marker는 24개에서 10개로 줄이고, selected callout은 짧은 직선 연결로 단순화했다. `docs/dashboard_full_design_review.md`에 focused re-review 내용을 추가했고, `npm run build` 통과, 3/4번 화면 재캡쳐 및 `NaN`, `undefined`, 깨진 문자 없음 확인.

- 3페이지 Frequency vs severity와 4페이지 Surface scenario layer를 한 번 더 후속 압축했다.
  - 반영 결과: 3번 matrix는 red severity cluster가 아직 강하게 보여 상위 severity 3개와 high-volume 대표 조건 4개만 남기도록 더 줄였고, 버블 반경도 낮췄다. 4번 surface layer는 selected callout의 중복 선을 제거하고 callout 박스 크기를 줄여 지도 위에서 덜 튀게 조정했다. `docs/dashboard_full_design_review.md`에 follow-up tightening 내용을 추가했고, `npm run build` 통과, 3/4번 화면 재캡쳐 및 `NaN`, `undefined`, 깨진 문자 없음 확인.
