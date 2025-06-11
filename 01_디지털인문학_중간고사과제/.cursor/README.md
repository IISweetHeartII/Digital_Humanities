# 한국영화배우 소셜네트워크 분석 프로젝트

본 프로젝트는 중앙대학교 디지털 인문학 수업의 중간고사 과제로, 영화진흥위원회(KOBIS) 데이터를 활용하여 한국 영화배우들의 소셜네트워크를 분석하는 것을 목표로 합니다.

## 프로젝트 구조

```
/project-root
  |- .cursor/
      |- README.md (프로젝트 설명)
      |- prompt.md (현재 연구 가설 및 목표 정리)
      |- analysis-plan.md (분석 단계 상세 계획)
  |- data/
      |- raw_movies.csv (영화ID, 제목, 감독, 출연진)
      |- network_edges.csv (actor1, actor2, 감독ID)
  |- scripts/
      |- data_collection.py (KOBIS 데이터 수집 스크립트)
      |- network_building.py (감독 기반 네트워크 생성)
      |- analysis.py (중심성 계산 및 결과 저장)
  |- reports/
      |- report.md (최종 제출 보고서)
      |- figures/ (네트워크 시각화 이미지 저장)
  |- requirements.txt (사용 라이브러리 목록)
```

## 주요 파일 설명
- `data_collection.py`: KOBIS Open API를 활용하여 영화 및 배우 데이터를 수집
- `network_building.py`: 수집된 데이터를 기반으로 배우-배우 네트워크 구축
- `analysis.py`: 네트워크 중심성 분석 및 시각화 수행

## 사용 기술
- Python
- NetworkX (네트워크 분석)
- Gephi (네트워크 시각화)
- Pandas (데이터 처리)
