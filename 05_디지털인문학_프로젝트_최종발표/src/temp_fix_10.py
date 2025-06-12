import pandas as pd
import os
import re

# 파일 경로 설정
CENTRALITIES_FILE = "data/processed/centralities.csv"
ADJUSTED_CENTRALITIES_FILE = "data/processed/adjusted_centralities.csv"
CHATGPT_LIST_FILE = "data/processed/chatgpt_philosophers_list.csv"
GEMINI_LIST_FILE = "data/processed/gemini_philosophers_list.csv"
OUTPUT_DIR = "data/processed/"

def get_name_map():
    """모든 이름 변환 규칙을 담은 딕셔너리를 반환합니다."""
    return {
        # 이니셜 및 축약형
        'T. Aquinas': 'Thomas Aquinas', 'Aquinas': 'Thomas Aquinas',
        'J.-J. Rousseau': 'Jean-Jacques Rousseau', 'Rousseau': 'Jean-Jacques Rousseau',
        'G. W. F. Hegel': 'Georg Wilhelm Friedrich Hegel', 'Hegel': 'Georg Wilhelm Friedrich Hegel',
        'S. Kierkegaard': 'Søren Kierkegaard', 'Kierkegaard': 'Søren Kierkegaard',
        'F. Nietzsche': 'Friedrich Nietzsche', 'Nietzsche': 'Friedrich Nietzsche',
        'L. Wittgenstein': 'Ludwig Wittgenstein', 'Wittgenstein': 'Ludwig Wittgenstein',
        'S. de Beauvoir': 'Simone de Beauvoir', 'Simone de Beauvoir': 'Simone de Beauvoir',
        'W. V. O. Quine': 'Willard Van Orman Quine', 'Quine': 'Willard Van Orman Quine',
        'C. S. Peirce': 'Charles Sanders Peirce', 'Peirce': 'Charles Sanders Peirce',
        'G. Leibniz': 'Gottfried Leibniz', 'Leibniz': 'Gottfried Leibniz',
        'F. de Saussure': 'Ferdinand de Saussure',
        'Descartes': 'René Descartes',
        'Kant': 'Immanuel Kant',
        'Marx': 'Karl Marx',
        'Heidegger': 'Martin Heidegger',
        'Sartre': 'Jean-Paul Sartre',
        'Locke': 'John Locke',
        'Hume': 'David Hume',
        'Russell': 'Bertrand Russell',
        'Popper': 'Karl Popper',
        'Kuhn': 'Thomas Kuhn',
        'Arendt': 'Hannah Arendt',
        'Dewey': 'John Dewey',
        'Rorty': 'Richard Rorty',
        'Gadamer': 'Hans-Georg Gadamer',
        'Foucault': 'Michel Foucault',
        'Deleuze': 'Gilles Deleuze',
        'Derrida': 'Jacques Derrida',
        'Rawls': 'John Rawls',
        
        # 한국어 이름 매핑
        '소크라테스': 'Socrates', '소크라테스 (Socrates)': 'Socrates',
        '플라톤': 'Plato', '플라톤 (Plato)': 'Plato',
        '아리스토텔레스': 'Aristotle', '아리스토텔레스 (Aristotle)': 'Aristotle',
        '공자': 'Confucius', '공자 (Confucius)': 'Confucius',
        '노자': 'Laozi', '노자 (Laozi)': 'Laozi',
        '헤겔': 'Georg Wilhelm Friedrich Hegel', '헤겔 (Georg Wilhelm Friedrich Hegel)': 'Georg Wilhelm Friedrich Hegel',
        '마르크스': 'Karl Marx', '마르크스 (Karl Marx)': 'Karl Marx',
        '니체': 'Friedrich Nietzsche', '니체 (Friedrich Nietzsche)': 'Friedrich Nietzsche',
        '하이데거': 'Martin Heidegger', '하이데거 (Martin Heidegger)': 'Martin Heidegger',
        '사르트르': 'Jean-Paul Sartre', '사르트르 (Jean-Paul Sartre)': 'Jean-Paul Sartre',
        '데카르트': 'René Descartes', '데카르트 (René Descartes)': 'René Descartes',
        '루소': 'Jean-Jacques Rousseau', '루소 (Jean-Jacques Rousseau)': 'Jean-Jacques Rousseau',
        '홉스': 'Thomas Hobbes', '홉스 (Thomas Hobbes)': 'Thomas Hobbes',
        '존 로크': 'John Locke', '존 로크 (John Locke)': 'John Locke',
        '버클리': 'George Berkeley', '버클리 (George Berkeley)': 'George Berkeley',
        '흄': 'David Hume', '흄 (David Hume)': 'David Hume',
        '스피노자': 'Baruch Spinoza', '스피노자 (Baruch Spinoza)': 'Baruch Spinoza',
        '라이프니츠': 'Gottfried Leibniz', '라이프니츠 (Gottfried Leibniz)': 'Gottfried Leibniz',
        '푸코': 'Michel Foucault', '푸코 (Michel Foucault)': 'Michel Foucault',
        '들뢰즈': 'Gilles Deleuze', '들뢰즈 (Gilles Deleuze)': 'Gilles Deleuze',
        '데리다': 'Jacques Derrida', '데리다 (Jacques Derrida)': 'Jacques Derrida',
        '비트겐슈타인': 'Ludwig Wittgenstein', '비트겐슈타인 (Ludwig Wittgenstein)': 'Ludwig Wittgenstein',
        '러셀': 'Bertrand Russell', '러셀 (Bertrand Russell)': 'Bertrand Russell',
        '프레게': 'Gottlob Frege', '프레게 (Gottlob Frege)': 'Gottlob Frege',
        '밀': 'John Stuart Mill', '밀 (John Stuart Mill)': 'John Stuart Mill',
        '벤담': 'Jeremy Bentham', '벤담 (Jeremy Bentham)': 'Jeremy Bentham',
        '키에르케고르': 'Søren Kierkegaard', '키에르케고르 (Søren Kierkegaard)': 'Søren Kierkegaard',
        '쇼펜하우어': 'Arthur Schopenhauer', '쇼펜하우어 (Arthur Schopenhauer)': 'Arthur Schopenhauer',
        '아퀴나스': 'Thomas Aquinas', '아퀴나스 (Thomas Aquinas)': 'Thomas Aquinas',
        '아우구스티누스': 'Augustine of Hippo', '아우구스티누스 (Augustine of Hippo)': 'Augustine of Hippo',
        '이븐 시나': 'Avicenna', '이븐 시나 (Avicenna)': 'Avicenna',
        '이븐 루시드': 'Averroes', '이븐 루시드 (Averroes)': 'Averroes',
        '모이세 마이모니데스': 'Moses Maimonides',
        '알 키디': 'Al-Kindi',
        '나가르주나': 'Nagarjuna',
        '찬드라키르티': 'Candrakīrti',
        '장자': 'Zhuangzi', '장자 (Zhuangzi)': 'Zhuangzi',
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
        '코넬 웨스트': 'Cornel West',
        'Machiavelli': 'Niccolò Machiavelli'
    }

def standardize_names(df, name_map):
    """DataFrame의 'Name' 컬럼을 표준화합니다."""
    if df is None or 'Name' not in df.columns:
        return df

    # 정규 표현식을 사용하여 괄호 안의 영어 이름 추출을 먼저 시도
    def extract_and_map(name):
        if not isinstance(name, str):
            return name
        
        # 1. 괄호 안의 영문 이름 추출
        match = re.search(r'\((.*?)\)', name)
        cleaned_name = match.group(1).strip() if match else name
        
        # 2. name_map을 사용하여 최종 표준화
        return name_map.get(cleaned_name, cleaned_name)

    df['Name'] = df['Name'].apply(extract_and_map)
    return df

def load_and_standardize(filepath, file_description, name_map):
    """파일을 로드하고 바로 이름 표준화를 적용합니다."""
    print(f"\n--- 처리 중: {file_description} ({filepath}) ---")
    if not os.path.exists(filepath):
        print(f"오류: 파일을 찾을 수 없습니다.")
        return None
    
    try:
        # AI 리스트의 '이름' 컬럼을 'Name'으로 변경
        df = pd.read_csv(filepath, encoding='utf-8')
        if '이름' in df.columns:
            df.rename(columns={'이름': 'Name'}, inplace=True)
        
        # 표준화 전에 이름 컬럼을 문자열로 변환
        df['Name'] = df['Name'].astype(str)
        
        df_standardized = standardize_names(df, name_map)
        print("성공: 파일 로드 및 이름 표준화 완료")
        return df_standardized
    except Exception as e:
        print(f"파일 처리 중 오류 발생: {e}")
        return None

def get_top_n(df, sort_by_col, rank_col_name, n=50):
    if df is None: return None
    df_sorted = df.sort_values(by=sort_by_col, ascending=False).head(n)
    df_sorted[rank_col_name] = range(1, len(df_sorted) + 1)
    return df_sorted

def compare_lists(df1, df2, df1_name, df2_name, rank1_col, rank2_col, output_filename):
    all_names = pd.concat([df1['Name'], df2['Name']]).unique()
    comparison_data = []
    for name in all_names:
        in_df1 = name in df1['Name'].values
        in_df2 = name in df2['Name'].values
        rank1 = df1[df1['Name'] == name][rank1_col].iloc[0] if in_df1 else None
        rank2 = df2[df2['Name'] == name][rank2_col].iloc[0] if in_df2 else None
        comparison_data.append({
            'Name': name,
            f'In_{df1_name}_Top50': in_df1,
            f'{df1_name}_Rank': rank1,
            f'In_{df2_name}_Top50': in_df2,
            f'{df2_name}_Rank': rank2
        })
    comparison_df = pd.DataFrame(comparison_data)
    comparison_df.to_csv(os.path.join(OUTPUT_DIR, output_filename), index=False, encoding='utf-8')
    print(f"성공: 비교 파일 저장 완료 -> {output_filename}")

if __name__ == "__main__":
    name_map = get_name_map()

    # 1. 모든 데이터 로드 및 이름 표준화
    centralities_df = load_and_standardize(CENTRALITIES_FILE, "표준 중심성", name_map)
    adjusted_df = load_and_standardize(ADJUSTED_CENTRALITIES_FILE, "조정된 중심성", name_map)
    chatgpt_df = load_and_standardize(CHATGPT_LIST_FILE, "ChatGPT 목록", name_map)
    gemini_df = load_and_standardize(GEMINI_LIST_FILE, "Gemini 목록", name_map)
    
    # 2. 랭크 부여
    top50_standard = get_top_n(centralities_df, 'In-Degree Centrality', 'Standard_Rank')
    top50_adjusted = get_top_n(adjusted_df, 'Adjusted_In_Degree_Centrality', 'Adjusted_Rank')
    # AI 목록은 이미 순위가 매겨져 있다고 가정하고 랭크를 부여
    if chatgpt_df is not None:
        chatgpt_df['ChatGPT_Rank'] = range(1, len(chatgpt_df) + 1)
    if gemini_df is not None:
        gemini_df['Gemini_Rank'] = range(1, len(gemini_df) + 1)

    # 3. 비교 실행
    compare_lists(top50_standard, top50_adjusted, "Standard", "Adjusted", 'Standard_Rank', 'Adjusted_Rank', "rankings_comparison_standard_vs_adjusted.csv")
    compare_lists(top50_standard, chatgpt_df, "Standard", "ChatGPT", 'Standard_Rank', 'ChatGPT_Rank', "rankings_comparison_standard_vs_chatgpt.csv")
    compare_lists(top50_standard, gemini_df, "Standard", "Gemini", 'Standard_Rank', 'Gemini_Rank', "rankings_comparison_standard_vs_gemini.csv")
    compare_lists(top50_adjusted, chatgpt_df, "Adjusted", "ChatGPT", 'Adjusted_Rank', 'ChatGPT_Rank', "rankings_comparison_adjusted_vs_chatgpt.csv")
    compare_lists(top50_adjusted, gemini_df, "Adjusted", "Gemini", 'Adjusted_Rank', 'Gemini_Rank', "rankings_comparison_adjusted_vs_gemini.csv")

    print("\n모든 비교 분석 완료.") 