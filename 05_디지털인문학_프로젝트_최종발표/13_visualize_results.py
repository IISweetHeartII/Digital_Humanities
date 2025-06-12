import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import platform

def set_korean_font():
    """OS에 맞게 한글 폰트를 설정합니다."""
    system_name = platform.system()
    if system_name == 'Windows':
        font_name = 'Malgun Gothic'
    elif system_name == 'Darwin': # macOS
        font_name = 'AppleGothic'
    else: # Linux
        font_name = 'NanumGothic'

    try:
        plt.rc('font', family=font_name)
        plt.rcParams['axes.unicode_minus'] = False
    except:
        print(f"'{font_name}' 폰트를 찾을 수 없습니다. 한글 폰트를 설치해주세요.")
        pass

def create_slope_chart(csv_path, output_filename, rank1_col, rank2_col, label1, label2, title):
    """범용 경사 차트 생성 함수"""
    NOT_IN_RANK = 55 # 순위권 밖을 나타내는 값
    
    try:
        df = pd.read_csv(csv_path)
        
        # 순위가 없는 경우(NaN)를 NOT_IN_RANK 값으로 채움
        df[rank1_col] = df[rank1_col].fillna(NOT_IN_RANK)
        df[rank2_col] = df[rank2_col].fillna(NOT_IN_RANK)

        # 순위 상승/하락/유지 따라 색상 결정
        def get_color(r1, r2):
            if r1 > r2: return 'blue'  # 순위 상승
            if r1 < r2: return 'red'   # 순위 하락
            return 'gray'            # 순위 유지

        df['color'] = df.apply(lambda row: get_color(row[rank1_col], row[rank2_col]), axis=1)

        plt.figure(figsize=(14, 22))
        
        for _, row in df.iterrows():
            r1, r2 = row[rank1_col], row[rank2_col]
            plt.plot([0, 1], [r1, r2], marker='o', color=row['color'], linewidth=1.2, markersize=4, alpha=0.8)
            
            # 이름이 너무 길면 자르기 (선택 사항)
            name = row['Name'] if len(row['Name']) < 25 else row['Name'][:22] + '...'

            if r1 != NOT_IN_RANK:
                 plt.text(0 - 0.03, r1, name, ha='right', va='center', fontsize=9)
            if r2 != NOT_IN_RANK:
                 plt.text(1 + 0.03, r2, name, ha='left', va='center', fontsize=9)
        
        plt.xticks([0, 1], [label1, label2], fontsize=14)
        plt.gca().invert_yaxis()
        plt.ylim(NOT_IN_RANK + 2, 0) # y축 범위 설정
        plt.xlim(-0.6, 1.6)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.title(title, fontsize=18, pad=20)
        plt.ylabel('순위 (Rank)', fontsize=12)
        
        # 범례 추가
        from matplotlib.lines import Line2D
        legend_elements = [Line2D([0], [0], color='blue', lw=2, label='순위 상승'),
                           Line2D([0], [0], color='red', lw=2, label='순위 하락'),
                           Line2D([0], [0], color='gray', lw=2, label='순위 유지/변동 없음')]
        plt.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.03), ncol=3, fontsize=12)
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.97])
        plt.savefig(output_filename, dpi=300)
        plt.close()
        print(f"성공: 경사 차트 저장 완료 -> {output_filename}")
    except Exception as e:
        print(f"오류: '{title}' 차트 생성 실패 - {e}")


def create_visualizations():
    """
    분석 결과를 바탕으로 시각화 자료를 생성하고 저장합니다.
    """
    # 경로 설정 (스크립트의 위치를 기준으로)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, 'data', 'processed')
    output_dir = os.path.join(base_dir, 'images')

    # 결과물 저장 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)

    # 한글 폰트 설정
    set_korean_font()

    # --- 1. 아이디어 1: 순위 변동 시각화 (5개 파일) ---
    comparison_files = [
        {'in': 'rankings_comparison_standard_vs_adjusted.csv', 'out': '1-1_slope_std_vs_adj.png', 
         'r1': 'Standard_Rank', 'r2': 'Adjusted_Rank', 'l1': '표준 중심성 순위', 'l2': '시간 보정 중심성 순위', 'title': '표준 vs 시간 보정 순위 변동'},
        {'in': 'rankings_comparison_standard_vs_chatgpt.csv', 'out': '1-2_slope_std_vs_chatgpt.png',
         'r1': 'Standard_Rank', 'r2': 'ChatGPT_Rank', 'l1': '표준 중심성 순위', 'l2': 'ChatGPT 추천 순위', 'title': '표준 vs ChatGPT 순위 비교'},
        {'in': 'rankings_comparison_standard_vs_gemini.csv', 'out': '1-3_slope_std_vs_gemini.png',
         'r1': 'Standard_Rank', 'r2': 'Gemini_Rank', 'l1': '표준 중심성 순위', 'l2': 'Gemini 추천 순위', 'title': '표준 vs Gemini 순위 비교'},
        {'in': 'rankings_comparison_adjusted_vs_chatgpt.csv', 'out': '1-4_slope_adj_vs_chatgpt.png',
         'r1': 'Adjusted_Rank', 'r2': 'ChatGPT_Rank', 'l1': '시간 보정 순위', 'l2': 'ChatGPT 추천 순위', 'title': '시간 보정 vs ChatGPT 순위 비교'},
        {'in': 'rankings_comparison_adjusted_vs_gemini.csv', 'out': '1-5_slope_adj_vs_gemini.png',
         'r1': 'Adjusted_Rank', 'r2': 'Gemini_Rank', 'l1': '시간 보정 순위', 'l2': 'Gemini 추천 순위', 'title': '시간 보정 vs Gemini 순위 비교'}
    ]

    for f in comparison_files:
        create_slope_chart(os.path.join(data_dir, f['in']), os.path.join(output_dir, f['out']), f['r1'], f['r2'], f['l1'], f['l2'], f['title'])

    # --- 2. 아이디어 3: 주요 철학자 순위 비교 (Grouped Bar Chart) ---
    try:
        key_philosophers = [
            'Immanuel Kant', 'Plato', 'Aristotle', 'Friedrich Nietzsche', 
            'Thomas Aquinas', 'Averroes', 'David Hume', 'Karl Marx',
            'Socrates', 'John Locke'
        ]
        
        # 필요한 모든 비교 데이터 로드
        df_std_adj = pd.read_csv(os.path.join(data_dir, 'rankings_comparison_standard_vs_adjusted.csv'))
        df_std_chat = pd.read_csv(os.path.join(data_dir, 'rankings_comparison_standard_vs_chatgpt.csv'))
        df_std_gem = pd.read_csv(os.path.join(data_dir, 'rankings_comparison_standard_vs_gemini.csv'))
        df_adj_chat = pd.read_csv(os.path.join(data_dir, 'rankings_comparison_adjusted_vs_chatgpt.csv'))
        df_adj_gem = pd.read_csv(os.path.join(data_dir, 'rankings_comparison_adjusted_vs_gemini.csv'))
        
        # 데이터 집계
        ranks = {}
        for name in key_philosophers:
            ranks[name] = {
                'Standard': df_std_adj[df_std_adj['Name'] == name]['Standard_Rank'].iloc[0] if not df_std_adj[df_std_adj['Name'] == name].empty else None,
                'Adjusted': df_std_adj[df_std_adj['Name'] == name]['Adjusted_Rank'].iloc[0] if not df_std_adj[df_std_adj['Name'] == name].empty else None,
                'ChatGPT': df_std_chat[df_std_chat['Name'] == name]['ChatGPT_Rank'].iloc[0] if not df_std_chat[df_std_chat['Name'] == name].empty else None,
                'Gemini': df_std_gem[df_std_gem['Name'] == name]['Gemini_Rank'].iloc[0] if not df_std_gem[df_std_gem['Name'] == name].empty else None,
            }

        df_ranks = pd.DataFrame.from_dict(ranks, orient='index').reset_index().rename(columns={'index': 'Name'})
        
        df_melted = df_ranks.melt(id_vars='Name', var_name='Rank_Type', value_name='Rank')
        df_melted['Rank'].fillna(0, inplace=True)

        plt.figure(figsize=(18, 10))
        # 색상 팔레트를 'bright'로 변경하여 대비를 높임
        ax = sns.barplot(x='Name', y='Rank', hue='Rank_Type', data=df_melted, palette='bright')
        
        plt.title('주요 철학자 순위 비교 (Grouped Bar Chart)', fontsize=18, pad=20)
        plt.xlabel('철학자 (Philosopher)', fontsize=12)
        plt.ylabel('순위 (Rank) - 0은 목록 미포함', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.legend(title='순위 유형 (Rank Type)')
        
        for p in ax.patches:
            if p.get_height() > 0:
                ax.annotate(f"{p.get_height():.0f}", 
                            (p.get_x() + p.get_width() / 2., p.get_height()), 
                            ha = 'center', va = 'center', 
                            xytext = (0, 9), 
                            textcoords = 'offset points')

        plt.tight_layout()
        bar_chart_path = os.path.join(output_dir, '3_key_philosophers_grouped_bar_chart.png')
        plt.savefig(bar_chart_path, dpi=300)
        plt.close()
        print(f"성공: 그룹 막대 차트 저장 완료 -> {bar_chart_path}")
    except Exception as e:
        print(f"오류: 그룹 막대 차트 생성 실패 - {e}")


if __name__ == '__main__':
    create_visualizations() 