import pandas as pd
import os
import re
import math

# 파일 경로 설정
PHILOSOPHERS_FILE = "data/raw/philosophers_by_century.csv"
CENTRALITIES_FILE = "data/processed/centralities.csv"

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

def extract_activity_year(date_string):
    """Date 문자열에서 활동 시기 연도 추출"""
    if pd.isna(date_string) or not isinstance(date_string, str):
        return None
    
    # 괄호 안의 4자리 숫자 또는 'BC' 다음에 나오는 숫자 추출
    match = re.search(r'(?:\(|BC\s*)(\d{1,4})', date_string)
    if match:
        try:
            year = int(match.group(1))
            # BC는 음수 연도로 처리 (BC 100년 -> -100)
            if 'BC' in date_string:
                 return -year
            return year
        except ValueError:
            pass # 숫자로 변환 실패 시 None 반환
            
    # 다른 형태의 연도 (예: 1800s) 처리 (간단히 첫 4자리 숫자로)
    match = re.search(r'\d{4}', date_string)
    if match:
        try:
            year = int(match.group(0))
            return year
        except ValueError:
            pass
            
    return None # 연도 추출 실패

# Adjusted Centrality 계산 함수
def calculate_adjusted_centrality(raw_centrality, activity_year):
    """Adjusted Centrality 계산 공식 적용"""
    CURRENT_YEAR = 2024
    
    if pd.isna(raw_centrality) or pd.isna(activity_year):
        return None # 계산 불가
    
    time_difference = CURRENT_YEAR - activity_year
    
    # 시간 차이가 0 이하이거나 로그 계산에 문제 발생 시 None 반환
    if time_difference <= 0:
        print(f"경고: 활동 시기({activity_year})가 현재 연도({CURRENT_YEAR})보다 크거나 같아 Adjusted Centrality 계산 불가. 이름: {activity_year}") # 디버깅 출력
        return None
        
    log_scale = math.log2(1 + time_difference)
    
    # 0으로 나누는 경우 방지
    if log_scale == 0:
         return None

    return raw_centrality / log_scale

# 1. 철학자 목록 및 중심성 결과 파일 로드
philosophers_df = load_csv(PHILOSOPHERS_FILE, "철학자 목록")
centrality_results_df = load_csv(CENTRALITIES_FILE, "중심성 계산 결과")

# 파일 로드 실패 시 종료
if philosophers_df is None or centrality_results_df is None:
    print("필요한 데이터 파일 로드에 실패하여 Adjusted Centrality 계산을 중단합니다.")
    exit(1)

# 2. 철학자 목록에서 이름과 활동 시기 추출
print("\n--- 활동 시기 추출 중 ---")

if "Name" not in philosophers_df.columns or "Date" not in philosophers_df.columns:
    print("오류: 철학자 목록 파일에 'Name' 또는 'Date' 컬럼이 없습니다.")
    exit(1)

philosophers_df['ActivityYear'] = philosophers_df['Date'].apply(extract_activity_year)

# 이름과 활동 시기 데이터만 선택
activity_years_df = philosophers_df[['Name', 'ActivityYear']].copy()

print(f"활동 시기 추출 완료. {activity_years_df['ActivityYear'].notna().sum()}개 항목에서 연도 추출 성공.")

# 3. 중심성 결과와 활동 시기 데이터 결합
print("\n--- 중심성 결과와 활동 시기 데이터 결합 중 ---")

# Name 컬럼을 기준으로 결합
merged_df = pd.merge(centrality_results_df, activity_years_df, on='Name', how='left')

print("데이터 결합 완료.")

# 4. Adjusted Centrality 계산
print("\n--- Adjusted Centrality 계산 중 ---")

# RawCentrality와 ActivityYear 컬럼이 있는지 확인
if "RawCentrality" not in merged_df.columns or "ActivityYear" not in merged_df.columns:
     print("오류: 'RawCentrality' 또는 'ActivityYear' 컬럼이 없어 Adjusted Centrality를 계산할 수 없습니다.")
     exit(1)

# Adjusted Centrality 계산 적용
# apply 함수와 axis=1을 사용하여 각 행에 대해 함수 적용
merged_df['AdjustedCentrality'] = merged_df.apply(
    lambda row: calculate_adjusted_centrality(row['RawCentrality'], row['ActivityYear']),
    axis=1
)

print("Adjusted Centrality 계산 완료.")

# 5. 업데이트된 결과 저장
print("\n--- 업데이트된 중심성 결과 저장 중 ---")

# AdjustedCentrality 컬럼이 추가된 DataFrame 저장
# 기존 중심성 결과 파일을 덮어씁니다.
merged_df.to_csv(CENTRALITIES_FILE, index=False, encoding='utf-8')

print(f"업데이트된 중심성 결과 저장 완료: {CENTRALITIES_FILE}")

print("스크립트 실행 완료.") 