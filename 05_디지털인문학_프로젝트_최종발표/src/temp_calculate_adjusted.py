import pandas as pd
import numpy as np
import os
import re

# 파일 경로 설정
CENTRALITIES_FILE = "data/processed/centralities.csv"
PHILOSOPHERS_DIR = "data/processed/by_century/"
OUTPUT_FILE = "data/processed/adjusted_centralities.csv" # Adjusted Centrality 결과를 저장할 파일

def parse_year(date_str):
    """
    날짜 문자열에서 기준 연도를 파싱합니다.
    BC는 음수로, 범위는 중간값으로 처리합니다.
    유효하지 않은 날짜는 None을 반환합니다.
    """
    if not isinstance(date_str, str):
        return None

    # 괄호 안의 내용 제거 (예: [a], [b])
    date_str = re.sub(r'\\[.*?\\]', '', date_str).strip()
    date_str = date_str.replace('*', '').strip() # * 문자 제거

    # 'died YYYY' 또는 'YYYY ?? YYYY' 또는 'YYYY-YYYY' 패턴 처리
    match = re.search(r'c?\.?\\s*(\\d+)\\s*(?:[?]{2}|-|CE|AD)?\\s*c?\.?\\s*(\\d+)?', date_str, re.IGNORECASE)
    if match:
        year1 = int(match.group(1))
        year2_str = match.group(2)

        if year2_str: # 범위가 있는 경우 (YYYY-YYYY 또는 YYYY??YYYY)
            year2 = int(year2_str)
            avg_year = (year1 + year2) / 2
        else: # 단일 연도 (c. YYYY, YYYY)
            avg_year = year1
        
        if 'BC' in date_str.upper():
            return -avg_year
        return avg_year
    
    # 다른 패턴 (단일 연도만 있는 경우 - 주로 앞쪽에 매칭됨)
    match_single = re.search(r'^\\s*c?\.?\\s*(\\d+)', date_str, re.IGNORECASE)
    if match_single:
        year = int(match_single.group(1))
        if 'BC' in date_str.upper():
            return -year
        return year

    return None

def calculate_adjusted_centrality():
    # 1. centralities.csv 파일 로드
    try:
        centralities_df = pd.read_csv(CENTRALITIES_FILE, encoding='utf-8')
        print(f"'{CENTRALITIES_FILE}' 파일 로드 성공.")
    except FileNotFoundError:
        print(f"오류: '{CENTRALITIES_FILE}' 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
        return
    except Exception as e:
        print(f"'{CENTRALITIES_FILE}' 파일 로드 중 오류 발생: {e}")
        return

    # 2. 철학자 활동 시기 데이터 통합 및 파싱
    philosophers_data = []
    philosophers_files = [f for f in os.listdir(PHILOSOPHERS_DIR) if f.startswith('philosophers_') and f.endswith('.csv')]
    
    if not philosophers_files:
        print(f"오류: '{PHILOSOPHERS_DIR}' 디렉토리에서 철학자 데이터 파일을 찾을 수 없습니다.")
        return

    for filename in philosophers_files:
        filepath = os.path.join(PHILOSOPHERS_DIR, filename)
        try:
            df = pd.read_csv(filepath, encoding='utf-8')
            philosophers_data.append(df[['Name', 'Date']])
        except Exception as e:
            print(f"'{filepath}' 파일 로드 중 오류 발생: {e}")
            continue

    if not philosophers_data:
        print("오류: 로드할 수 있는 철학자 데이터 파일이 없습니다.")
        return

    all_philosophers_df = pd.concat(philosophers_data, ignore_index=True)
    all_philosophers_df.drop_duplicates(subset=['Name'], inplace=True)
    print(f"총 {len(all_philosophers_df)}명의 철학자 활동 시기 데이터 로드 완료.")

    # 'Date' 컬럼의 문자열을 파싱하여 'Year' 컬럼 생성
    all_philosophers_df['Year'] = all_philosophers_df['Date'].apply(parse_year)

    # 3. 중심성 데이터와 활동 시기 데이터 병합
    merged_df = pd.merge(centralities_df, all_philosophers_df[['Name', 'Year']], on='Name', how='left')
    print("중심성 데이터와 철학자 활동 시기 데이터 병합 완료.")

    # 4. Adjusted Centrality 계산
    current_year = 2024
    
    # Year 컬럼을 numeric으로 변환, 에러는 NaN으로 처리
    merged_df['Year'] = pd.to_numeric(merged_df['Year'], errors='coerce')

    # 시간 차이 계산
    time_diff = current_year - merged_df['Year']

    # 분모 계산: log2(1 + 시간 차이)
    # 시간 차이가 0 이하인 경우(Year가 2024 이상) 분모가 정의되지 않으므로, where를 사용해 NaN으로 처리
    log_denominator = np.log2(1 + time_diff.where(time_diff > 0))

    # Adjusted In-Degree Centrality 계산
    merged_df['Adjusted_In_Degree_Centrality'] = merged_df['In-Degree Centrality'] / log_denominator
    
    print("Adjusted In-Degree Centrality 계산 완료.")
    
    # 결과 미리보기 (디버깅용, 유효한 값이 있는 행을 상위로)
    print("\nAdjusted Centrality 계산 결과 상위 5개 (유효한 값 기준):")
    print(merged_df.sort_values(by='Adjusted_In_Degree_Centrality', ascending=False)[['Name', 'In-Degree Centrality', 'Year', 'Adjusted_In_Degree_Centrality']].head())

    # 5. 결과 저장
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    merged_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
    print(f"\n조정된 중심성 결과가 '{OUTPUT_FILE}'에 성공적으로 저장되었습니다.")

if __name__ == "__main__":
    calculate_adjusted_centrality() 