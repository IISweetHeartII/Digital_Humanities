# Digital_Humanities: 철학자 지적 영향력 분석 프로젝트

## 1. 프로젝트 개요

본 프로젝트는 위키피디아 데이터를 기반으로 구축된 철학자 네트워크를 분석하여 철학자들의 지적 영향력을 계량적으로 평가하고, 이를 다각적인 관점에서 비교 분석하는 디지털 인문학 연구입니다. 특히, 전통적인 네트워크 중심성 지표와 함께 철학자의 활동 시기를 고려한 '시간 보정 중심성'이라는 새로운 지표를 도입하고, 최신 AI 모델(ChatGPT, Gemini)이 평가하는 철학자 순위와 비교하여 그 의미와 한계를 탐색하는 것을 목표로 합니다.

## 2. 프로젝트 목표 및 주요 연구 질문

- 철학자들의 지적 영향력을 측정하고 비교할 수 있는 효과적인 계량적 방법은 무엇인가?
- 철학자의 활동 시기를 고려한 '시간 보정 중심성'은 기존 중심성 지표와 비교하여 어떤 새로운 통찰을 제공하는가?
- 데이터 기반의 계량적 분석 결과와 AI(LLM)가 제시하는 철학자 영향력 순위는 어떤 유사점과 차이점을 보이는가? 이러한 차이는 어디에서 기인하는가?
- 네트워크 시각화(Gephi)를 통해 철학자들 간의 연결 구조와 핵심 커뮤니티를 어떻게 파악할 수 있는가?

## 3. 데이터 및 방법론

### 3.1. 사용 데이터

- **철학자 네트워크 데이터**: 위키피디아 데이터를 기반으로 구축된 철학자 간 인용/언급 관계 네트워크 (`mention_network.csv`, `centrality_raw.csv` 등 활용)
- **철학자 활동 시기 데이터**: `philosophers_by_century.csv`
- **LLM 생성 철학자 목록**: ChatGPT 및 Gemini가 제시한 영향력 있는 철학자 목록 (`docs/chatgpt_philosophers_list.md`, `docs/gemini_philosophers_list.md` 등)

### 3.2. 주요 분석 지표

- **내차수 중심성 (In-Degree Centrality)**: 다른 철학자로부터 얼마나 많이 인용/언급되었는지를 나타내는 지표.
- **시간 보정 내차수 중심성 (Adjusted In-Degree Centrality)**: 내차수 중심성을 철학자의 활동 시기를 고려하여 보정한 지표. (`시간 보정 점수 = 내차수 중심성 / log2(1 + (2024 - 활동 연도))`)
- **AI 인지 중심성 (AI Perceived Centrality)**: LLM이 제시한 순위를 바탕으로 변환한 지표.

### 3.3. 핵심 분석 과정

1.  **데이터 정제 및 전처리**:
    - 다양한 출처의 데이터 통합 및 형식 일관성 확보.
    - **이름 표준화**: 철학자 이름 표기법 불일치 문제 해결 (가장 중요하고 어려웠던 과정 중 하나. `temp_fix_10.py`와 같은 임시 스크립트를 통해 여러 단계에 걸쳐 해결).
    - 파일 인코딩 문제 해결 (`UnicodeDecodeError` 등).
2.  **중심성 계산**:
    - 기본 내차수 중심성 계산.
    - 시간 보정 내차수 중심성 계산 (이 과정에서 `NaN` 값 발생 문제 해결).
3.  **순위 비교 분석**:
    - 표준 내차수 중심성, 시간 보정 내차수 중심성, ChatGPT 추천, Gemini 추천 등 다양한 기준에 따른 철학자 순위 생성.
    - 각 순위 목록 비교를 통해 공통점, 차이점, 순위 변동 등을 분석.
4.  **시각화**:
    - Python 라이브러리(`matplotlib`, `seaborn`)를 활용한 비교 분석 결과 시각화 (경사 차트, 그룹 막대 차트 등).
    - Gephi를 활용한 핵심 철학자 네트워크 시각화 (노드 크기: 중심성, 색상: 커뮤니티).
5.  **보고서 작성**: 분석 결과 및 해석을 종합하여 최종 보고서 작성.

## 4. 프로젝트 수행 중 발생한 주요 문제 및 해결 과정

본 프로젝트는 계획부터 최종 결과 도출까지 여러 기술적, 논리적 문제에 직면했으며, 이를 해결하는 과정은 다음과 같았습니다.

- **파일 경로 및 작업 디렉토리 불일치**: 스크립트 실행 초기 `FileNotFoundError`가 빈번하게 발생. `os.path.join` 사용 및 작업 디렉토리 통일로 해결.
- **시간 보정 중심성 `NaN` 값 발생**: `08_calculate_adjusted_centrality.py` 실행 후 결과가 모두 `NaN`으로 나오는 오류 발생. 원본 데이터 경로 오류 및 인코딩 문제(`UnicodeDecodeError`)를 단계적으로 해결 (`temp_fix_08.py` 활용).
- **철학자 이름 표준화의 어려움**: 다양한 데이터 소스(중심성 데이터, AI 생성 목록) 간 철학자 이름 표기법이 달라(`T. Aquinas` vs `Thomas Aquinas`), 초기 비교 분석 시 공통 철학자가 거의 없는 문제 발생.
  - 초기에는 단순 매핑 시도했으나 실패.
  - 문제의 복잡성을 인지하고, **`temp_fix_10.py`** 와 같은 임시 스크립트에서 **(1) 모든 데이터 로드 → (2) 포괄적인 `name_map`을 사용한 최우선 이름 표준화 → (3) 이후 분석 수행**이라는 명확한 파이프라인으로 재설계하여 최종 해결. 이 과정은 프로젝트 성공의 핵심적인 부분이었음.
- **시각화 개선 요구**: 초기 시각화 결과물에 대한 사용자 피드백(경사 차트 개선, 업셋 플롯 불필요, 막대 차트 가독성 향상)을 반영하여 스크립트(`13_visualize_results.py`)를 대대적으로 수정.

## 5. 주요 결과 및 시각화 산출물

### 5.1. 핵심 분석 결과

- **시간 보정 중심성의 효과**: 고대/중세 철학자의 순위는 하락하고, 근현대 철학자(사울 크립키, 피터 싱어 등)의 순위가 상승하여 '동시대적 영향력'을 더 잘 반영함을 확인.
- **데이터 기반 분석 vs. AI 추천**:
  - **공통점**: 칸트, 아리스토텔레스, 플라톤 등 핵심 철학자들은 모든 목록에서 높은 순위를 차지.
  - **차이점**: 데이터 분석은 아베로에스 등 이슬람 철학자의 중요성을 부각한 반면, AI 추천은 시몬 드 보부아르, 한나 아렌트 등 여성 철학자나 대중적 인지도가 높은 인물을 포함하는 경향. 이는 AI 학습 데이터의 특성에 기인하는 것으로 해석.
- **Gephi 네트워크 분석**: 상위 철학자들(표준 내차수 중심성 기준 49명) 간의 연결 구조 시각화를 통해, 특정 철학자(예: Plato, Aristotle)를 중심으로 형성된 커뮤니티와 그들의 영향력 범위를 가시적으로 확인.

### 5.2. 주요 시각화 자료 (`images` 폴더)

- `1-1_rank_change_slope_standard_vs_adjusted.png` (및 유사 경사 차트 4개): 다양한 기준 간 철학자 순위 변동 시각화.
- `3_key_philosophers_grouped_bar_chart.png`: 주요 철학자들의 목록별 순위 비교.
- `gephi_network_visualization.png`: Gephi로 생성한 핵심 철학자 네트워크 시각화.

## 6. 최종 산출물

- **최종 보고서**: `디지털인문학_최종보고서.md` (프로젝트의 모든 과정, 분석 결과, 해석, 결론 포함)
- **Gephi용 데이터**:
  - `data/processed/nodes_gephi.csv` (노드 파일, 49명, Weight는 표준 내차수 중심성)
  - `data/processed/edges_gephi.csv` (엣지 파일)
- **주요 분석 스크립트**: `src` 폴더 (아래 폴더 구조 참고)
- **시각화 이미지**: `images` 폴더

## 7. 폴더 구조

```
./05_디지털인문학_프로젝트_최종발표/
├── data/
│   ├── processed/          # 전처리 및 분석 결과 데이터
│   │   ├── nodes_gephi.csv
│   │   ├── edges_gephi.csv
│   │   ├── rankings_comparison_standard_vs_adjusted.csv (등 비교 파일 5개)
│   │   ├── top_50_in-degree-centralities_standard.csv
│   │   ├── adjusted_centralities.csv
│   │   └── ... (기타 중간 산출물)
│   ├── raw/                # 원본 데이터
│   │   ├── centrality_raw.csv
│   │   ├── mention_network.csv
│   │   └── philosophers_by_century.csv
│   └── gephi/              # Gephi 프로젝트 파일 저장 (사용자 생성)
├── docs/                   # 문서 파일
│   ├── chatgpt_philosophers_list.md
│   ├── gemini_philosophers_list.md
│   └── ... (기타 참고 문서)
├── images/                 # 생성된 시각화 이미지
│   ├── 1-1_rank_change_slope_standard_vs_adjusted.png
│   ├── 1-2_rank_change_slope_standard_vs_chatgpt.png
│   ├── 1-3_rank_change_slope_standard_vs_gemini.png
│   ├── 1-4_rank_change_slope_adjusted_vs_chatgpt.png
│   ├── 1-5_rank_change_slope_adjusted_vs_gemini.png
│   ├── 3_key_philosophers_grouped_bar_chart.png
│   └── gephi_network_visualization.png
├── src/                    # 분석 스크립트 및 소스코드
│   ├── (예상: 01_filter_top_philosophers.py)
│   ├── (예상: 08_calculate_adjusted_centrality.py 또는 temp_fix_08.py)
│   ├── (예상: 10_compare_centrality_rankings.py 또는 temp_fix_10.py)
│   ├── 13_visualize_results.py
│   ├── 14_prepare_gephi_data.py
│   └── ... (기타 분석 스크립트)
├── 디지털인문학_최종보고서.md # 최종 결과 보고서
├── README.md                 # 본 파일
├── TODO.md                   # 초기 아이디어 및 작업 계획
├── TODO2.md                  # 시각화 계획
├── TODO_final.md             # 최종 작업 지침
├── doing1.md                 # 프로젝트 진행 기록 1
├── doing2.md                 # 프로젝트 진행 기록 2 (보고서 초안)
├── doing3.md                 # 프로젝트 진행 기록 3 (문제 해결 중심)
└── doing4.md                 # 프로젝트 진행 기록 4 (시각화 및 Gephi 준비)
```

## 8. 향후 개선 방향 (보고서 내용 기반)

- 인용의 '내용'을 분석하는 질적 연구 추가.
- 분석 대상을 다른 학문 분야로 확장.
- 더 정교한 이름 동음이의어 처리 및 표준화 알고리즘 적용.

---

이 README 파일은 프로젝트의 전체 여정을 담고 있으며, `TODO` 및 `doing` 문서들의 핵심 내용을 통합하여 작성되었습니다.
