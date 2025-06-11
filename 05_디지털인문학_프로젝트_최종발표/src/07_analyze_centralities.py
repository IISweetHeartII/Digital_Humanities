import pandas as pd
import os

# 파일 경로 설정
CENTRALITIES_FILE = "data/processed/centralities.csv"
PHILOSOPHERS_FILE = "data/raw/philosophers_by_century.csv" # 철학자 목록 파일 추가
OUTPUT_FILE = "data/processed/top_50_centralities_standard.csv" # 출력 파일 경로 설정

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

def analyze_centralities(centrality_results_df, philosophers_df):
    """
    중심성 계산 결과와 철학자 목록을 결합하여 각 중심성 지표별 상위 N명의 철학자를 추출하고 저장합니다.
    주요 목표는 In-Degree Centrality를 포함한 다양한 표준 중심성 지표에 대한 상위 랭킹을 파악하는 것입니다.
    """
    # 2. 중심성 결과와 철학자 목록 결합 (세기 정보 추가)
    print("\n--- 중심성 결과와 철학자 목록 결합 중 ---")

    # 철학자 목록에서 'Name'과 'Century' 컬럼만 선택
    if "Name" not in philosophers_df.columns or "Century" not in philosophers_df.columns:
        print("오류: 철학자 목록 파일에 'Name' 또는 'Century' 컬럼이 없습니다.")
        return
    philosophers_info = philosophers_df[['Name', 'Century']].copy()

    # Name 컬럼을 기준으로 중심성 결과와 결합
    # left_on='Name', right_on='Name'으로 명시적 설정
    merged_df = pd.merge(centrality_results_df, philosophers_info, on='Name', how='left')

    print("데이터 결합 완료.")

    # 3. 각 중심성 지표별 상위 N명 추출 및 결과 저장
    print("\n--- 각 중심성 지표별 상위 50명 추출 및 저장 중 ---")

    # 분석할 중심성 컬럼 목록 (RawCentrality는 유의미한 값이 없어 제외)
    centrality_columns = [
        'Calculated_In_Degree_Count', # In-Degree의 원시 값 (정규화 전)
        'In-Degree Centrality',       # 정규화된 In-Degree (피인용 또는 영향력)
        'Out-Degree Centrality',
        'Closeness Centrality',
        'Betweenness Centrality',
        'Eigenvector Centrality'
    ]
    # 'RawCentrality' 컬럼은 분석에 유의미한 값을 가지고 있지 않으므로 제외합니다.

    TOP_N = 50

    # 결과를 저장할 DataFrame 리스트
    top_n_results_list = []

    for column in centrality_columns:
        if column in merged_df.columns:
            print(f"  - '{column}' 기준 상위 {TOP_N}명 추출 중...")
            
            # 해당 컬럼 기준으로 내림차순 정렬하고 상위 N개 추출
            top_n_philosophers = merged_df.sort_values(by=column, ascending=False).head(TOP_N).copy()
            
            # 결과를 저장할 DataFrame에 추가 (어떤 중심성 기준인지 나타내는 컬럼 추가)
            top_n_philosophers['Centrality_Type'] = column
            top_n_results_list.append(top_n_philosophers)
        else:
            print(f"경고: '{column}' 컬럼이 결합된 데이터에 없습니다. 이 기준으로는 상위 인물을 추출할 수 없습니다.")

    # 모든 상위 N명 결과를 하나의 DataFrame으로 합침
    if top_n_results_list:
        all_top_n_results_df = pd.concat(top_n_results_list, ignore_index=True)
        
        # 필요한 컬럼만 선택하여 순서 재정렬
        final_columns = ['Centrality_Type', 'Name', 'Century'] + centrality_columns
        final_top_n_df = all_top_n_results_df[[col for col in final_columns if col in all_top_n_results_df.columns]]
        
        # 결과를 CSV 파일로 저장
        final_top_n_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
        
        print(f"\n상위 {TOP_N}명 인물 추출 및 결과 저장 완료: {OUTPUT_FILE}")
        print("이 파일에는 각 중심성 지표별 상위 인물 목록이 포함되어 있습니다.")
    else:
        print("경고: 상위 인물을 추출할 수 있는 유효한 중심성 컬럼이 없습니다. 출력 파일이 생성되지 않았습니다.")

if __name__ == "__main__":
    # 1. 데이터 파일 로드
    centrality_results_df = load_csv(CENTRALITIES_FILE, "중심성 계산 결과")
    philosophers_df = load_csv(PHILOSOPHERS_FILE, "철학자 목록")

    # 파일 로드 실패 시 종료
    if centrality_results_df is None or philosophers_df is None:
        print("필요한 데이터 파일 로드에 실패하여 상위 인물 추출을 중단합니다.")
        exit(1)
    
    analyze_centralities(centrality_results_df, philosophers_df)
    
    print("스크립트 실행 완료.") 