# 프로젝트 진행 상황 (Doing 1)

## 1. 연구 개요

이 프로젝트는 Wikipedia 데이터를 활용하여 철학자들 간의 영향력 네트워크를 분석하고, 특히 AI가 인지하는 철학자의 영향력을 탐색하며, 최종적으로 학술 보고서를 작성하는 디지털 인문학 연구입니다.

## 2. 데이터 수집 및 전처리 (기존)

- 철학자 목록 및 언급 관계 데이터가 수집 및 전처리되어 있습니다. (이전 프로젝트에서 진행)
- 세기별 철학자 데이터가 분리되어 있습니다. (이전 프로젝트에서 진행)

## 3. AI 주관 기반 중심성 데이터 생성 및 처리 (완료)

- **AI (나)**: LLM(GPT-4o, Gemini)이 선정한 철학자 목록을 파싱하여 기존 철학자 데이터와 매핑하고, 'AI Perceived Centrality' 지표를 계산하여 `data/processed/top_50_adjusted_centralities.csv` 파일을 성공적으로 생성했습니다.
- **사용자 (나)**: LLM(GPT-4o 등)을 활용하여 영향력 있는 철학자 목록을 생성하고, 이를 텍스트 파일(`docs/chatgpt_philosophers_list.md`, `docs/gemini_philosophers_list.md`)로 저장했으며, 이 파일들은 분석을 위해 CSV 형태로 변환되었습니다.

## 4. AI 주관 기반 중심성 계산 및 비교

- `05_디지털인문학_프로젝트_최종발표/src/08_calculate_ai_perceived_centrality.py` 스크립트를 사용하여 'AI 주관 기반 중심성'을 계산하고, 상위 50명을 `data/processed/top_50_adjusted_centralities.csv`에 저장했습니다.
- `05_디지털인문학_프로젝트_최종발표/src/10_compare_centrality_rankings.py` 스크립트를 수정하여 'In-Degree Centrality'와 'Combined_AI_Perceived_Centrality' 간의 순위 비교를 수행하고, `data/processed/centrality_ranking_comparison.csv` 파일을 생성했습니다.
- `05_디지털인문학_프로젝트_최종발표/src/12_visualize_centrality_comparison.py` 스크립트를 수정 및 실행하여 다음 시각화 파일을 생성했습니다:
  - `data/processed/visualizations/top50_overlap_analysis.png`
  - `data/processed/visualizations/top50_rank_comparison_scatter.png`

## 다음 단계

- 최종 보고서 작성 및 분석 결과 해석
