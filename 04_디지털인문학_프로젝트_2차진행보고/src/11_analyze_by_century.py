import pandas as pd
import os

# 파일 경로 설정
CENTRALITIES_FILE = "data/processed/centralities.csv"
PHILOSOPHERS_FILE = "data/raw/philosophers_by_century.csv"
OUTPUT_DIR_CENTURY = "data/processed/by_century/"
CENTURY_SUMMARY_FILE = os.path.join(OUTPUT_DIR_CENTURY, "century_analysis_summary.csv")

# 출력 디렉토리가 없으면 생성
os.makedirs(OUTPUT_DIR_CENTURY, exist_ok=True)

def load_csv(filepath, file_description):
    """CSV 파일을 로드하고 기본 정보를 출력"""
    if not os.path.exists(filepath):
        print(f"오류: {file_description} 파일이 존재하지 않습니다: {filepath}")
        return None
        
    print(f"\n--- {file_description} 파일 확인 중: {filepath} ---")
    try:
        # 다양한 인코딩 시도
        encodings = ['utf-8', 'cp1252', 'latin1', 'iso-8859-1']
        df = None
        for encoding in encodings:
            try:
                df = pd.read_csv(filepath, encoding=encoding)
                print(f"성공: {encoding} 인코딩으로 파일 로드됨")
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            print("오류: 지원되는 인코딩으로 파일을 읽을 수 없습니다")
            return None
            
        print(f"총 {len(df)} 행, {len(df.columns)} 열 로드 완료")
        return df
    except Exception as e:
        print(f"{file_description} 파일 로딩 오류: {e}")
        return None

# 1. 필요한 데이터 파일 로드
centrality_df = load_csv(CENTRALITIES_FILE, "중심성 결과")
philosophers_df = load_csv(PHILOSOPHERS_FILE, "철학자 목록")

# 파일 로드 실패 시 종료
if centrality_df is None or philosophers_df is None:
    print("필요한 데이터 파일 로드에 실패하여 시대별 분석을 중단합니다.")
    exit(1)

# 'Name'과 'Century' 컬럼만 선택
philosophers_century = philosophers_df[['Name', 'Century']].copy()

# 2. 중심성 데이터와 세기 정보 결합
# 혹시 모를 중복 이름 제거 (philosophers_century 파일에서)
philosophers_century = philosophers_century.drop_duplicates(subset=['Name'])

merged_df = pd.merge(centrality_df, philosophers_century, on='Name', how='left')

print("\n--- 중심성 데이터와 세기 정보 결합 완료 ---")

# 세기 정보가 없는 항목 확인
# philosophers_by_century.csv에 없는 이름은 Century가 NaN이 됩니다.
missing_century_count = merged_df['Century'].isna().sum()
if missing_century_count > 0:
    print(f"경고: {missing_century_count}개 항목에서 세기 정보가 누락되었습니다.")
    # 누락된 항목을 제외하고 분석 진행
    analyis_df = merged_df.dropna(subset=['Century', 'AdjustedCentrality']).copy()
else:
     analyis_df = merged_df.dropna(subset=['AdjustedCentrality']).copy()

print(f"시대별 분석 대상 항목 수: {len(analyis_df)}")

# 3. 세기별 요약 통계 계산
print("\n--- 세기별 요약 통계 계산 중 ---")

# 유효한 숫자형 컬럼만 선택하여 평균 계산
numeric_cols = analyis_df.select_dtypes(include='number').columns
summary_by_century = analyis_df.groupby('Century')[numeric_cols.tolist() + ['Name']].agg({
    'Name': 'count',
    'RawCentrality': 'mean',
    'In-Degree Centrality': 'mean',
    'Out-Degree Centrality': 'mean',
    'Closeness Centrality': 'mean',
    'Betweenness Centrality': 'mean',
    'Eigenvector Centrality': 'mean',
    'AdjustedCentrality': 'mean'
}).rename(columns={'Name': 'Philosopher_Count'})

# Adjusted Centrality 기준으로 내림차순 정렬 (세기 자체의 중요도)
summary_by_century = summary_by_century.sort_values(by='AdjustedCentrality', ascending=False)

print("세기별 요약 통계 계산 완료.")

# 4. 각 세기별 Adjusted Centrality 상위 N명 추출 및 저장
print("\n--- 각 세기별 Adjusted Centrality 상위 N명 추출 중 ---")

TOP_N_PER_CENTURY = 10 # 각 세기별 상위 10명

for century, century_df in analyis_df.groupby('Century'):
    # 해당 세기 내에서 Adjusted Centrality 기준으로 정렬
    top_philosophers_in_century = century_df.sort_values(by='AdjustedCentrality', ascending=False).head(TOP_N_PER_CENTURY)
    
    # 결과 파일명 설정 (세기 이름을 파일명으로 사용)
    # 파일명에 사용할 수 없는 문자 제거 또는 대체
    safe_century_name = str(century).replace('/', '_').replace('?', '').replace(' ','_')
    century_top_n_file = os.path.join(OUTPUT_DIR_CENTURY, f"top_{TOP_N_PER_CENTURY}_adjusted_centrality_{safe_century_name}.csv")
    
    # 해당 세기의 상위 N명 결과를 CSV 파일로 저장
    top_philosophers_in_century.to_csv(century_top_n_file, index=False, encoding='utf-8')
    print(f"  - '{century}' 세기 상위 {TOP_N_PER_CENTURY}명 저장 완료: {century_top_n_file}")

print("각 세기별 Adjusted Centrality 상위 N명 추출 및 저장 완료.")

# 5. 세기별 요약 통계 결과 저장
print("\n--- 세기별 요약 통계 결과 저장 중 ---")

summary_by_century.to_csv(CENTURY_SUMMARY_FILE, encoding='utf-8')

print(f"세기별 요약 통계 결과 저장 완료: {CENTURY_SUMMARY_FILE}")

print("스크립트 실행 완료.") 