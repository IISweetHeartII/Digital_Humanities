import pandas as pd
import os

# 파일 경로 설정
CENTRALITIES_FILE = "data/processed/centralities.csv"
ADJUSTED_CENTRALITIES_FILE = "data/processed/adjusted_centralities.csv"
CHATGPT_LIST_FILE = "data/processed/chatgpt_philosophers_list.csv"
GEMINI_LIST_FILE = "data/processed/gemini_philosophers_list.csv"

# 출력 파일 경로 (각 비교별)
OUTPUT_DIR = "data/processed/" # 모든 비교 CSV가 저장될 디렉토리

def load_csv(filepath, file_description):
    """CSV 파일을 로드하고 기본 정보를 출력"""
    if not os.path.exists(filepath):
        print(f"오류: {file_description} 파일이 존재하지 않습니다: {filepath}")
        return None

    print(f"\n--- {file_description} 파일 확인 중: {filepath} ---")
    try:
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
        if 'Name' not in df.columns:
            print("오류: 파일에 'Name' 컬럼이 없습니다.")
            return None
        return df
    except Exception as e:
        print(f"{file_description} 파일 로딩 오류: {e}")
        return None

def get_top_n_philosophers(df, centrality_col, n=50):
    """
    주어진 DataFrame에서 특정 중심성 컬럼 기준으로 상위 n명의 철학자를 추출하고 랭크를 부여합니다.
    """
    if df is None or centrality_col not in df.columns:
        return None
    
    # NaN 값은 제외하고, 중심성 기준으로 내림차순 정렬
    top_n_df = df.dropna(subset=[centrality_col]).sort_values(
        by=centrality_col, ascending=False
    ).head(n).copy()
    
    # 랭크 부여 (1부터 시작)
    top_n_df[f'{centrality_col}_Rank'] = range(1, len(top_n_df) + 1)
    return top_n_df[['Name', f'{centrality_col}_Rank']]

def get_ai_list_philosophers(df, n=50):
    """
    AI 철학자 목록 DataFrame에서 상위 n명의 철학자를 추출하고 랭크를 부여합니다.
    (리스트의 순서가 곧 랭크)
    """
    if df is None or 'Name' not in df.columns:
        return None
    
    # 리스트의 순서대로 랭크 부여
    ai_list_df = df.head(n).copy()
    ai_list_df['AI_List_Rank'] = range(1, len(ai_list_df) + 1)
    return ai_list_df[['Name', 'AI_List_Rank']]


def perform_and_save_comparison(df1_top_n, df2_top_n, df1_name, df2_name, output_filename):
    """
    두 상위 N명 목록을 비교하고 결과를 CSV 파일로 저장합니다.
    """
    if df1_top_n is None or df2_top_n is None:
        print(f"비교에 필요한 데이터가 부족하여 '{output_filename}' 저장을 건너뜁니다.")
        return

    # 두 목록의 모든 고유한 이름 추출
    all_names = pd.concat([df1_top_n['Name'], df2_top_n['Name']]).unique()

    comparison_data = []
    
    # 컬럼 이름이 중복되지 않도록 접미사 추가
    rank_col_df1 = df1_top_n.columns[1] # e.g., 'In-Degree Centrality_Rank'
    rank_col_df2 = df2_top_n.columns[1] # e.g., 'Adjusted_In_Degree_Centrality_Rank' or 'AI_List_Rank'

    for name in all_names:
        in_df1 = name in df1_top_n['Name'].values
        in_df2 = name in df2_top_n['Name'].values
        
        rank1 = df1_top_n[df1_top_n['Name'] == name][rank_col_df1].iloc[0] if in_df1 else None
        rank2 = df2_top_n[df2_top_n['Name'] == name][rank_col_df2].iloc[0] if in_df2 else None
        
        comparison_data.append({
            'Name': name,
            f'In_{df1_name}_Top50': in_df1,
            f'{df1_name}_Rank': rank1,
            f'In_{df2_name}_Top50': in_df2,
            f'{df2_name}_Rank': rank2
        })

    comparison_df = pd.DataFrame(comparison_data)
    
    # 결과 저장
    os.makedirs(os.path.dirname(os.path.join(OUTPUT_DIR, output_filename)), exist_ok=True)
    comparison_df.to_csv(os.path.join(OUTPUT_DIR, output_filename), index=False, encoding='utf-8')
    print(f"'{df1_name}'와 '{df2_name}' 비교 결과가 '{output_filename}'에 성공적으로 저장되었습니다.")


if __name__ == "__main__":
    # 1. 모든 원본 데이터 로드
    centralities_df = load_csv(CENTRALITIES_FILE, "표준 중심성 데이터")
    adjusted_centralities_df = load_csv(ADJUSTED_CENTRALITIES_FILE, "조정된 중심성 데이터")
    chatgpt_list_df = load_csv(CHATGPT_LIST_FILE, "ChatGPT 철학자 목록")
    gemini_list_df = load_csv(GEMINI_LIST_FILE, "Gemini 철학자 목록")

    # 필요한 DataFrame이 모두 로드되었는지 확인
    if any(df is None for df in [centralities_df, adjusted_centralities_df, chatgpt_list_df, gemini_list_df]):
        print("필요한 데이터 파일 로드에 실패하여 비교 분석을 중단합니다.")
        exit(1)

    # 2. 각 데이터 소스에서 상위 50명 추출
    top50_standard = get_top_n_philosophers(centralities_df, 'In-Degree Centrality', n=50)
    top50_adjusted = get_top_n_philosophers(adjusted_centralities_df, 'Adjusted_In_Degree_Centrality', n=50)
    top50_chatgpt = get_ai_list_philosophers(chatgpt_list_df, n=50)
    top50_gemini = get_ai_list_philosophers(gemini_list_df, n=50)

    # 3. 각 비교 수행 및 결과 저장
    print("\n--- 상위 50명 목록 비교 분석 시작 ---")

    # 1. In-Degree Centrality (표준 중심성) 와 Adjusted In-Degree Centrality의 비교
    perform_and_save_comparison(
        top50_standard, top50_adjusted,
        "Standard_In_Degree", "Adjusted_In_Degree",
        "rankings_comparison_standard_vs_adjusted.csv"
    )

    # 2. In-Degree Centrality (표준 중심성) 와 ChatGPT 철학자 목록의 비교
    perform_and_save_comparison(
        top50_standard, top50_chatgpt,
        "Standard_In_Degree", "ChatGPT_List",
        "rankings_comparison_standard_vs_chatgpt.csv"
    )

    # 3. In-Degree Centrality (표준 중심성) 와 Gemini 철학자 목록의 비교
    perform_and_save_comparison(
        top50_standard, top50_gemini,
        "Standard_In_Degree", "Gemini_List",
        "rankings_comparison_standard_vs_gemini.csv"
    )
    
    # 4. Adjusted In-Degree Centrality 와 ChatGPT 철학자 목록의 비교
    perform_and_save_comparison(
        top50_adjusted, top50_chatgpt,
        "Adjusted_In_Degree", "ChatGPT_List",
        "rankings_comparison_adjusted_vs_chatgpt.csv"
    )

    # 5. Adjusted In-Degree Centrality 와 Gemini 철학자 목록의 비교
    perform_and_save_comparison(
        top50_adjusted, top50_gemini,
        "Adjusted_In_Degree", "Gemini_List",
        "rankings_comparison_adjusted_vs_gemini.csv"
    )

    print("\n모든 비교 분석 완료.")
    print("스크립트 실행 완료.") 