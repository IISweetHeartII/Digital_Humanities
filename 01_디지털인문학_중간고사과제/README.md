# 한국 영화 감독-배우 네트워크 분석

깃허브 주소 : git@github.com:IISweetHeartII/cau_univ_class.git
하위 폴더 : digital_humanities

본 프로젝트는 KOBIS(영화진흥위원회) 데이터를 기반으로 한국 영화의 감독-배우 네트워크를 분석합니다.

## 프로젝트 구조

```
digital_humanities/
├── data/
│   ├── raw/          # KOBIS 원본 데이터(csv 파일)
│   ├── gephi/        # 정제된 데이터(csv 파일), Gephi 분석 파일
│   └── img/          # 이미지 자료
├── documents/        # 연구 문서(목차, 작업)
├── src/             # 소스 코드(python)
├── requirements.txt  # 프로젝트 의존성
└── README.md        # 프로젝트 문서
```

## 설치 방법

1. Python 3.9 이상 설치
2. 의존성 설치:
   ```bash
   pip install -r requirements.txt
   ```

## 데이터 수집

- KOBIS Open API를 활용한 영화 정보 수집
- 감독별 참여 배우 정보 수집
- 데이터 전처리 및 정제

## 네트워크 분석

- NetworkX를 활용한 네트워크 구축
- 중심성(Centrality) 분석
  - Degree Centrality
  - Eigenvector Centrality
  - Closeness Centrality
- 커뮤니티 탐지
- Gephi를 활용한 시각화
