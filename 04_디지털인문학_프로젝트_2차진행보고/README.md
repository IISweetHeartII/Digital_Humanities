# Digital_Humanities

## 프로젝트 개요

이 프로젝트는 Wikipedia 데이터를 활용하여 철학자들 간의 영향력 네트워크를 분석하고, 시간(세기/시대)에 따른 네트워크 특성 변화를 탐색하는 디지털 인문학 연구입니다.

## 파일 및 폴더 구조

프로젝트는 다음과 같은 구조로 구성되어 있습니다.

```
./
├── data/
│   ├── checkpoints/       # 데이터 수집 중간 저장 파일
│   ├── processed/       # 전처리 및 분석 결과 데이터
│   │   ├── by_century/  # 세기별 분리 데이터 및 분석 결과
│   │   └── visualizations/ # 시각화 이미지 저장
│   └── raw/             # 초기 수집 원본 데이터
├── docs/
│   ├── 디지털인문학_2차발표.md # 2차 발표 자료
│   └── report_guideline.md # 최종 보고서 가이드라인 및 체크리스트
├── src/
│   ├── 01_namelist.py       # 철학자 목록 수집
│   ├── 02_search_name_from_wiki.py # 언급 관계 데이터 수집
│   ├── 03_verify_data.py    # 데이터 검증
│   ├── 04_split_data_by_century.py # 세기별 데이터 분리
│   ├── 05_create_network_graph.py # 네트워크 그래프 생성
│   ├── 06_calculate_centralities.py # 표준 중심성 계산
│   ├── 07_analyze_centralities.py # 표준 중심성 결과 분석 (Top 50 등)
│   ├── 08_calculate_adjusted_centrality.py # Adjusted 중심성 계산
│   ├── 09_analyze_adjusted_centralities.py # Adjusted 중심성 결과 분석 (Top 50 등)
│   ├── 11_analyze_by_century.py # 세기별 분석
│   └── 12_visualize_centrality_comparison.py # 중심성 비교 시각화
└── README.md            # 프로젝트 개요 및 파일 구조 (현재 파일)
```

## 진행 상황

데이터 수집, 전처리, 네트워크 분석 및 주요 중심성 계산, 그리고 전체 및 시대별/세기별 결과 분석까지 완료되었습니다. 현재 주요 결과 시각화 및 보고서 작성을 진행 중입니다.

프로젝트 상세 내용은 [`docs/report_guideline.md`](docs/report_guideline.md) 및 [`docs/디지털인문학_2차발표.md`](docs/디지털인문학_2차발표.md) 파일을 참고해주세요.
