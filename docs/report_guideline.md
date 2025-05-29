# 디지털 인문학 프로젝트 보고서 가이드라인 및 체크리스트

## 1. 서론

- 프로젝트의 목표 및 연구 질문 제시
  - Wikipedia 데이터를 활용하여 철학자 간의 영향력 네트워크 분석
  - 각 철학자가 다른 철학자들에게 얼마나 언급되는지 측정
  - 시간(세기/시대)에 따른 네트워크 특성 변화 탐색
- 연구의 배경 및 중요성 (왜 철학자 네트워크 분석을 하는가?)
- 보고서의 구성 소개

## 2. 연구 방법론

### 2.1 데이터 수집

- 데이터 출처: Wikipedia 철학자 목록 및 개별 철학자 페이지
- 사용 도구 및 기술: Python (requests, BeautifulSoup, pandas 라이브러리)
- 수집 과정:
  - `src/01_namelist.py` 스크립트를 이용한 철학자 목록 및 기본 정보 추출 (`data/raw/philosophers_by_century.csv` 생성)
  - `src/02_search_name_from_wiki.py` 스크립트를 이용한 각 철학자 페이지 크롤링 및 언급 관계 추출 (`data/processed/mention_edges.csv`, `data/processed/centrality_raw.csv` 생성)
- 수집된 데이터 규모: 총 3468명의 철학자, 총 언급 관계 (엣지) 수 (추후 `mention_edges.csv` 파일 확인 후 업데이트 필요)
- 데이터 수집 시 겪었던 문제점 및 해결 과정 (예: 크롤링 속도 제한, 연결 오류, 인코딩 문제, 스크립트 중단 및 체크포인트 활용 등 상세 기술)

### 2.2 데이터 전처리 및 조직

- 데이터 파일 설명:
  - `data/raw/philosophers_by_century.csv`: 이름, 생몰년 정보, 세기, Wikipedia 링크
  - `data/processed/centrality_raw.csv`: 이름, Raw Centrality (다른 페이지에서 언급된 총 횟수)
  - `data/processed/mention_edges.csv`: Source 철학자 → Target 철학자 언급 관계 목록
  - `data/processed/centralities.csv`: 이름, Raw Centrality 및 계산된 다양한 중심성 지표 (In-Degree, Out-Degree, Closeness, Betweenness, Eigenvector, Adjusted Centrality)
  - `data/processed/top_50_centralities_standard.csv`: 표준 중심성별 상위 50명 목록
  - `data/processed/top_50_adjusted_centralities.csv`: Adjusted Centrality 기준 상위 50명 목록
- 데이터 정리 및 필터링 과정 (예: 중복 제거, 유효하지 않은 데이터 처리)
- `src/03_verify_data.py` 스크립트를 활용한 데이터 최종 확인 과정 기술
- `src/04_split_data_by_century.py` 스크립트를 활용한 시대별/세기별 데이터 분리 과정 기술 (결과 파일 위치: `data/processed/by_century/`)
- 'Date' 컬럼에서 '활동시기' (Activity Year) 추출 및 `data/processed/centralities.csv` 파일에 추가 과정 기술 (`src/08_calculate_adjusted_centrality.py` 스크립트)

### 2.3 네트워크 분석

- 네트워크 정의:
  - 노드 (Node): 각 철학자
  - 엣지 (Edge): 한 철학자의 Wikipedia 페이지에서 다른 철학자의 이름이 언급된 경우 (방향성 있음: 언급한 철학자 → 언급된 철학자)
- 사용 도구 및 기술: Python (NetworkX 라이브러리)
- 중심성 지표 계산 과정 기술:
  - `src/05_create_network_graph.py` 스크립트를 활용한 네트워크 그래프 생성
  - `src/06_calculate_centralities.py` 스크립트를 활용한 표준 중심성 (In-Degree, Out-Degree, Closeness, Betweenness, Eigenvector) 계산
  - `src/08_calculate_adjusted_centrality.py` 스크립트를 활용한 Adjusted Centrality 계산
- Adjusted Centrality 공식 설명 및 필요성 (오래 활동한 철학자의 Raw Centrality 편향 보정)

## 3. 결과 및 분석

- 전체 네트워크 분석 결과:

  - 주요 중심성 지표 (Raw Centrality, Adjusted Centrality 포함)별 상위 N명 철학자 목록 및 순위 비교 (`data/processed/top_50_centralities_standard.csv`, `data/processed/top_50_adjusted_centralities.csv` 파일 활용)
  - Raw Centrality와 Adjusted Centrality 결과 간의 주요 차이점 및 시사점 분석

    - 표준 중심성 Top 50과 Adjusted 중심성 Top 50 목록에 **모두 포함된 철학자들**의 순위 비교 분석

    | Name                  | Standard Rank | Adjusted Rank |
    | :-------------------- | :------------ | :------------ |
    | Jan Zwicky            | 1.0           | 1.0           |
    | Damon Young           | 2.0           | 14.0          |
    | Arthur M. Young       | 3.0           | 15.0          |
    | John Edwin Smith      | 4.0           | 16.0          |
    | Xu Liangying          | 5.0           | 17.0          |
    | W. D. Wright          | 6.0           | 18.0          |
    | Ursula Wolf           | 7.0           | 19.0          |
    | Susan R. Wolf         | 8.0           | 20.0          |
    | Jan WoleÅski          | 9.0           | 21.0          |
    | Karol WojtyÅa         | 10.0          | 22.0          |
    | Richard Dien Winfield | 11.0          | 23.0          |
    | Mark Wilson           | 12.0          | 24.0          |
    | Jan Willis            | 13.0          | 25.0          |
    | Frederick Wilhelmsen  | 14.0          | 26.0          |
    | Alan R. White         | 15.0          | 27.0          |
    | Alan White            | 16.0          | 28.0          |
    | Robert B. Westbrook   | 17.0          | 29.0          |
    | Abhinavagupta         | 19.0          | 13.0          |
    | Parashara             | 23.0          | 12.0          |
    | Markandeya            | 24.0          | 11.0          |
    | Lopamudra             | 25.0          | 10.0          |
    | Ashtavakra            | 30.0          | 9.0           |
    | Agastya               | 32.0          | 8.0           |
    | Benson Mates          | 33.0          | 7.0           |
    | Immanuel Kant         | 55.0          | 3.0           |
    | David Hume            | 61.0          | 2.0           |
    | Anselm                | 62.0          | 46.0          |
    | Karl Popper           | 85.0          | 42.0          |
    | Jacques Derrida       | 278.0         | 44.0          |
    | Isaac Newton          | 292.0         | 40.0          |

  - 전체 네트워크 특성 요약 (노드/엣지 수, 평균 연결 정도 등)

- 시대별/세기별 분석 결과:
  - 각 시대별 철학자 수 분포 및 특징
  - 각 시대별 네트워크의 특징 (예: 평균 연결 정도 변화 추이)
  - 각 시대 _내에서_ Adjusted Centrality가 높은 철학자 목록 및 특징 분석
  - 시대별 중심성 지표 결과 비교 및 해석
- 주요 발견 및 통찰 제시

## 4. 결론

- 연구 결과 요약
- 연구 질문에 대한 답변
- 연구의 한계점 및 추가 연구 방향 제안

## 5. 참고문헌 (사용한 데이터 출처, 라이브러리 문서, 코드 등)

## 6. 부록 (선택 사항)

- 주요 코드 스니펫 또는 스크립트 목록 첨부 (src/ 폴더 구조 참고)
- 생성된 데이터 파일 목록 및 설명
- 네트워크 시각화 이미지 첨부

---

## 프로젝트 진행 체크리스트

### 데이터 수집 및 전처리

- [x] Wikipedia 철학자 목록 수집 및 기본 정보 CSV 저장 (`data/raw/philosophers_by_century.csv`) - `src/01_namelist.py`
- [x] 각 철학자 Wikipedia 페이지 크롤링 및 언급 관계 추출 (`data/processed/mention_edges.csv`, `data/processed/centrality_raw.csv`) - `src/02_search_name_from_wiki.py`
- [x] 데이터 수집 중단 시 이어서 실행 기능 구현 및 완료
- [x] 수집된 데이터 최종 확인 (이상치, 잘못된 데이터 등) - `src/03_verify_data.py`
- [x] 'Date' 컬럼 파싱하여 '활동시기' 데이터 확보 - `src/08_calculate_adjusted_centrality.py`
- [x] 시대별/세기별로 데이터 분리 - `src/04_split_data_by_century.py`

### 네트워크 분석 및 결과 추출

- [x] Python에 NetworkX 등 네트워크 분석 라이브러리 설치
- [x] 네트워크 그래프 생성 - `src/05_create_network_graph.py`
- [x] 표준 중심성 (In-Degree, Out-Degree, Closeness, Betweenness, Eigenvector) 계산 - `src/06_calculate_centralities.py`
- [x] '활동시기' 데이터를 기반으로 Adjusted Centrality 계산 - `src/08_calculate_adjusted_centrality.py`
- [x] 전체 결과 요약 및 주요 철학자 순위 정리 (표준 중심성 상위 50명 추출) - `src/07_analyze_centralities.py`
- [x] Adjusted Centrality 기준 상위 50명 추출 - `src/09_analyze_adjusted_centralities.py`

### 결과 분석 및 보고서 작성

- [x] Raw Centrality와 Adjusted Centrality 결과 비교 분석 (상위 목록 비교 및 순위 변화 파악)
- [x] 시대별/세기별 분석 결과 정리 (각 세기별 Adjusted Centrality 상위 인물 등 분석)
- [x] 결과 시각화 (필요시 Python 라이브러리 활용하여 이미지 생성)
- [ ] 보고서 초안 작성 (서론, 방법론, 결과, 결론 등)
- [ ] 보고서 검토 및 수정
- [ ] 최종 보고서 제출 준비 (코드, 데이터 포함)

---

**참고:**

- 모든 스크립트 파일은 `src/` 폴더에 있습니다.
- 원본 데이터는 `data/raw/`에, 처리된 데이터 및 결과는 `data/processed/`에 저장됩니다.
- 데이터 수집 체크포인트 파일은 `data/checkpoints/`에 저장되었습니다.

이제 이 가이드라인에 따라 다음 단계인 **Raw Centrality와 Adjusted Centrality 결과 비교 분석** 또는 **시대별/세기별 분석 결과 정리**를 진행할 수 있습니다. 어떤 작업부터 시작할까요?
