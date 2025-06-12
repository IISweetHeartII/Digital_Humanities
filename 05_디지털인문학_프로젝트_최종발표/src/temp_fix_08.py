import pandas as pd
import numpy as np
import os
import re

# 파일 경로 설정
CENTRALITIES_FILE = "data/processed/centralities.csv"
PHILOSOPHERS_FILE = "data/raw/philosophers_by_century.csv" # 철학자 활동 시기 원본 데이터
OUTPUT_FILE = "data/processed/adjusted_centralities.csv" # Adjusted Centrality 결과를 저장할 파일

def parse_year(date_str):
    """
    날짜 문자열에서 기준 연도를 파싱합니다.
    BC는 음수로, 범위는 중간값으로 처리합니다.
    유효하지 않은 날짜는 None을 반환합니다.
    """
    if not isinstance(date_str, str):
        return None

    date_str = date_str.strip()

    # BC 처리
    is_bc = 'BC' in date_str.upper()
    date_str = re.sub(r'(?i)bc', '', date_str).strip()

    # YYYY–YYYY 형식 처리
    parts = re.split(r'–|-|\?{2}', date_str)
    years = [int(re.search(r'\d+', part).group()) for part in parts if re.search(r'\d+', part)]

    if not years:
        return None

    avg_year = sum(years) / len(years)
    
    return -avg_year if is_bc else avg_year

def load_csv_with_encoding_attempts(filepath, file_description):
    """다양한 인코딩을 시도하여 CSV 파일을 로드합니다."""
    encodings = ['utf-8', 'cp1252', 'latin1', 'iso-8859-1']
    for encoding in encodings:
        try:
            df = pd.read_csv(filepath, encoding=encoding)
            print(f"성공: '{filepath}' 파일을 '{encoding}' 인코딩으로 로드했습니다.")
            return df
        except UnicodeDecodeError:
            continue
    print(f"오류: 모든 인코딩 시도 실패. '{filepath}' 파일을 읽을 수 없습니다.")
    return None

def calculate_adjusted_centrality():
    # 1. centralities.csv 파일 로드
    centralities_df = load_csv_with_encoding_attempts(CENTRALITIES_FILE, "중심성 결과")
    if centralities_df is None:
        return

    # 2. 철학자 활동 시기 데이터 로드 및 파싱
    all_philosophers_df = load_csv_with_encoding_attempts(PHILOSOPHERS_FILE, "철학자 활동 시기")
    if all_philosophers_df is None:
        return

    all_philosophers_df.drop_duplicates(subset=['Name'], inplace=True)
    # 'Date' 컬럼 대신 'Century' 컬럼을 사용하도록 수정
    all_philosophers_df['Activity Year'] = all_philosophers_df['Century'].apply(parse_year)
    print(f"총 {len(all_philosophers_df)}명의 철학자 활동 시기 데이터 파싱 완료.")


    # 3. 중심성 데이터와 활동 시기 데이터 병합
    merged_df = pd.merge(centralities_df, all_philosophers_df[['Name', 'Activity Year']], on='Name', how='left')
    print("중심성 데이터와 철학자 활동 시기 데이터 병합 완료.")

    # 4. Adjusted Centrality 계산
    current_year = 2024
    merged_df['Activity Year'] = pd.to_numeric(merged_df['Activity Year'], errors='coerce')
    time_diff = current_year - merged_df['Activity Year']
    log_denominator = np.log2(1 + time_diff.where(time_diff > 0))
    merged_df['Adjusted_In_Degree_Centrality'] = merged_df['In-Degree Centrality'] / log_denominator
    
    print("Adjusted In-Degree Centrality 계산 완료.")
    
    print("\nAdjusted Centrality 계산 결과 상위 5개 (유효한 값 기준):")
    print(merged_df.sort_values(by='Adjusted_In_Degree_Centrality', ascending=False)[['Name', 'In-Degree Centrality', 'Activity Year', 'Adjusted_In_Degree_Centrality']].head())

    # 5. 결과 저장
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    merged_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
    print(f"\n조정된 중심성 결과가 '{OUTPUT_FILE}'에 성공적으로 저장되었습니다.")

if __name__ == "__main__":
    calculate_adjusted_centrality() 