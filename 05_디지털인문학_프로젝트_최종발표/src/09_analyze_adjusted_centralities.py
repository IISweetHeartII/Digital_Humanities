import pandas as pd
import os

# 파일 경로 설정
CENTRALITIES_FILE = "data/processed/adjusted_centralities.csv"
ADJUSTED_TOP50_FILE = "data/processed/top_50_adjusted_in-degree-centralities.csv"

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
        # Adjusted_In_Degree_Centrality 컬럼이 있는지 확인
        if 'Adjusted_In_Degree_Centrality' not in df.columns:
            print("오류: 'Adjusted_In_Degree_Centrality' 컬럼이 파일에 없습니다.")
            return None
            
        return df
    except Exception as e:
        print(f"{file_description} 파일 로딩 오류: {e}")
        return None

# 1. 중심성 결과 파일 로드
centrality_results_df = load_csv(CENTRALITIES_FILE, "조정된 중심성 계산 결과")

# 파일 로드 실패 시 종료
if centrality_results_df is None:
    print("필요한 데이터 파일 로드에 실패하여 Adjusted Centrality 분석을 중단합니다.")
    exit(1)

# 2. Adjusted Centrality 기준으로 내림차순 정렬하고 상위 50명 선택
print("\n--- Adjusted In-Degree Centrality 기준 상위 50명 추출 중 ---")

# 유효한 Adjusted_In_Degree_Centrality 값이 있는 행만 선택
top_adjusted_centrality_df = centrality_results_df.dropna(subset=['Adjusted_In_Degree_Centrality']).sort_values(by='Adjusted_In_Degree_Centrality', ascending=False).head(50)

print("Adjusted In-Degree Centrality 기준 상위 50명 추출 완료.")

# 3. 결과를 새 CSV 파일로 저장
print("\n--- Adjusted In-Degree Centrality 상위 50명 결과 저장 중 ---")

top_adjusted_centrality_df.to_csv(ADJUSTED_TOP50_FILE, index=False, encoding='utf-8')

print(f"Adjusted In-Degree Centrality 상위 50명 결과 저장 완료: {ADJUSTED_TOP50_FILE}")

print("스크립트 실행 완료.") 