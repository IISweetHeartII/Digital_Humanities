import pandas as pd
import os
import re

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

        # AI 리스트의 '이름' 컬럼을 'Name'으로 변경
        if '이름' in df.columns:
            df.rename(columns={'이름': 'Name'}, inplace=True)

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

def clean_ai_name(name):
    """
    AI 생성 목록의 철학자 이름을 정제합니다.
    - 괄호 안의 영문 이름을 추출합니다.
    - 약어나 다른 표기를 통일합니다.
    """
    if not isinstance(name, str):
        return name

    original_name = name
    # 괄호 안의 이름 추출 (e.g., "소크라테스 (Socrates)" -> "Socrates")
    match = re.search(r'\((.*?)\)', name)
    if match:
        name = match.group(1).strip()

    # AI 리스트의 이름과 중심성 데이터의 이름을 매핑
    name_map = {
        # 이니셜 및 축약형
        'T. Aquinas': 'Thomas Aquinas',
        'J.-J. Rousseau': 'Jean-Jacques Rousseau',
        'G. W. F. Hegel': 'Georg Wilhelm Friedrich Hegel',
        'S. Kierkegaard': 'Søren Kierkegaard',
        'F. Nietzsche': 'Friedrich Nietzsche',
        'L. Wittgenstein': 'Ludwig Wittgenstein',
        'S. de Beauvoir': 'Simone de Beauvoir',
        'W. V. O. Quine': 'Willard Van Orman Quine',
        'C. S. Peirce': 'Charles Sanders Peirce',
        'G. Leibniz': 'Gottfried Leibniz',
        'F. de Saussure': 'Ferdinand de Saussure',
        'Descartes': 'René Descartes',
        'Kant': 'Immanuel Kant',
        'Hegel': 'Georg Wilhelm Friedrich Hegel',
        'Marx': 'Karl Marx',
        'Nietzsche': 'Friedrich Nietzsche',
        'Heidegger': 'Martin Heidegger',
        'Sartre': 'Jean-Paul Sartre',
        'Locke': 'John Locke',
        'Hume': 'David Hume',
        'Russell': 'Bertrand Russell',
        'Popper': 'Karl Popper',
        'Kuhn': 'Thomas Kuhn',
        'Aquinas': 'Thomas Aquinas',
        'Arendt': 'Hannah Arendt',
        'Peirce': 'Charles Sanders Peirce',
        'Dewey': 'John Dewey',
        'Rorty': 'Richard Rorty',
        'Gadamer': 'Hans-Georg Gadamer',
        'Foucault': 'Michel Foucault',
        'Deleuze': 'Gilles Deleuze',
        'Derrida': 'Jacques Derrida',
        'Rawls': 'John Rawls',
        
        # 한국어 이름 매핑
        '소크라테스': 'Socrates',
        '플라톤': 'Plato',
        '아리스토텔레스': 'Aristotle',
        '공자': 'Confucius',
        '노자': 'Laozi',
        '헤겔': 'Georg Wilhelm Friedrich Hegel',
        '마르크스': 'Karl Marx',
        '니체': 'Friedrich Nietzsche',
        '하이데거': 'Martin Heidegger',
        '사르트르': 'Jean-Paul Sartre',
        '데카르트': 'René Descartes',
        '루소': 'Jean-Jacques Rousseau',
        '홉스': 'Thomas Hobbes',
        '존 로크': 'John Locke',
        '버클리': 'George Berkeley',
        '흄': 'David Hume',
        '스피노자': 'Baruch Spinoza',
        '라이프니츠': 'Gottfried Leibniz',
        '푸코': 'Michel Foucault',
        '들뢰즈': 'Gilles Deleuze',
        '데리다': 'Jacques Derrida',
        '비트겐슈타인': 'Ludwig Wittgenstein',
        '러셀': 'Bertrand Russell',
        '프레게': 'Gottlob Frege',
        '밀': 'John Stuart Mill',
        '벤담': 'Jeremy Bentham',
        '키에르케고르': 'Søren Kierkegaard',
        '쇼펜하우어': 'Arthur Schopenhauer',
        '아퀴나스': 'Thomas Aquinas',
        '아우구스티누스': 'Augustine of Hippo',
        '이븐 시나': 'Avicenna',
        '이븐 루시드': 'Averroes',
        '모이세 마이모니데스': 'Moses Maimonides',
        '알 키디': 'Al-Kindi',
        '나가르주나': 'Nagarjuna',
        '찬드라키르티': 'Candrakīrti',
        '장자': 'Zhuangzi',
        '한나 아렌트': 'Hannah Arendt',
        '시몬 드 보부아르': 'Simone de Beauvoir',
        '주디스 버틀러': 'Judith Butler',
        '찰스 퍼스': 'Charles Sanders Peirce',
        '윌리엄 제임스': 'William James',
        '존 듀이': 'John Dewey',
        '리차드 로티': 'Richard Rorty',
        '가다머': 'Hans-Georg Gadamer',
        '칼 포퍼': 'Karl Popper',
        '토마스 쿤': 'Thomas Kuhn',
        '아이리스 머독': 'Iris Murdoch',
        '코넬 웨스트': 'Cornel West'
    }
    
    # This part of the logic is improved to handle names with and without parentheses
    base_name = original_name.split('(')[0].strip()
    
    # Check for a direct match in the map first (for full names or already clean names)
    if original_name in name_map:
        return name_map[original_name]
    # Check for a match of the base name (e.g., "소크라테스" from "소크라테스 (Socrates)")
    if base_name in name_map:
        return name_map[base_name]

    # If no mapping is found, return the name extracted from parentheses if it exists,
    # otherwise return the original name.
    return name

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

    # AI 리스트 이름 정제
    if chatgpt_list_df is not None:
        chatgpt_list_df['Name'] = chatgpt_list_df['Name'].apply(clean_ai_name)
    if gemini_list_df is not None:
        gemini_list_df['Name'] = gemini_list_df['Name'].apply(clean_ai_name)

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