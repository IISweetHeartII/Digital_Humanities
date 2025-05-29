import pandas as pd
import os

# 파일 경로 설정
STANDARD_TOP50_FILE = "data/processed/top_50_centralities_standard.csv"
ADJUSTED_TOP50_FILE = "data/processed/top_50_adjusted_centralities.csv"
COMPARISON_OUTPUT_FILE = "data/processed/centrality_ranking_comparison.csv"

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
        # 'Name' 컬럼이 있는지 확인
        if 'Name' not in df.columns:
            print("오류: 파일에 'Name' 컬럼이 없습니다.")
            return None
            
        return df
    except Exception as e:
        print(f"{file_description} 파일 로딩 오류: {e}")
        return None

# 1. 표준 및 Adjusted 중심성 상위 50명 파일 로드
standard_top50_df = load_csv(STANDARD_TOP50_FILE, "표준 중심성 상위 50명")
adjusted_top50_df = load_csv(ADJUSTED_TOP50_FILE, "Adjusted 중심성 상위 50명")

# 파일 로드 실패 시 종료
if standard_top50_df is None or adjusted_top50_df is None:
    print("필요한 상위 50명 목록 파일 로드에 실패하여 비교 분석을 중단합니다.")
    exit(1)

# 비교를 위해 'Name' 컬럼만 사용
standard_names = standard_top50_df['Name']
adjusted_names = adjusted_top50_df['Name']

# 두 목록에 포함된 모든 고유한 이름 추출
all_names = pd.concat([standard_names, adjusted_names]).unique()

# 비교 결과를 저장할 DataFrame 생성
comparison_data = []

print("\n--- 상위 50명 목록 비교 중 ---")

for name in all_names:
    in_standard = name in standard_names.values
    in_adjusted = name in adjusted_names.values
    
    standard_rank = standard_names[standard_names == name].index[0] + 1 if in_standard else None
    adjusted_rank = adjusted_names[adjusted_names == name].index[0] + 1 if in_adjusted else None
    
    comparison_data.append({
        'Name': name,
        'In_Standard_Top50': in_standard,
        'Standard_Rank': standard_rank,
        'In_Adjusted_Top50': in_adjusted,
        'Adjusted_Rank': adjusted_rank
    })

comparison_df = pd.DataFrame(comparison_data)

print("비교 분석 완료.")

# 3. 비교 분석 결과 저장
print("\n--- 비교 분석 결과 저장 중 ---")

comparison_df.to_csv(COMPARISON_OUTPUT_FILE, index=False, encoding='utf-8')

print(f"비교 분석 결과 저장 완료: {COMPARISON_OUTPUT_FILE}")

print("스크립트 실행 완료.") 