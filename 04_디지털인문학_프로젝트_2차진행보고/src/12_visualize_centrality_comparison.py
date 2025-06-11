import pandas as pd
import matplotlib.pyplot as plt
import os

# 파일 경로 설정
COMPARISON_FILE = "data/processed/centrality_ranking_comparison.csv"
OUTPUT_DIR_VIS = "data/processed/visualizations/"

# 출력 디렉토리가 없으면 생성
os.makedirs(OUTPUT_DIR_VIS, exist_ok=True)

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

# 1. 비교 분석 결과 파일 로드
comparison_df = load_csv(COMPARISON_FILE, "중심성 순위 비교 결과")

# 파일 로드 실패 시 종료
if comparison_df is None:
    print("필요한 비교 분석 결과 파일 로드에 실패하여 시각화를 중단합니다.")
    exit(1)

# 2. 상위 50명 목록 중복 분석 시각화
print("\n--- Generating Top 50 List Overlap Visualization ---")

# 각 그룹에 속하는 철학자 수 계산
only_standard = comparison_df[(comparison_df['In_Standard_Top50'] == True) & (comparison_df['In_Adjusted_Top50'] == False)].shape[0]
only_adjusted = comparison_df[(comparison_df['In_Standard_Top50'] == False) & (comparison_df['In_Adjusted_Top50'] == True)].shape[0]
common = comparison_df[(comparison_df['In_Standard_Top50'] == True) & (comparison_df['In_Adjusted_Top50'] == True)].shape[0]

labels = ['Only Standard Top 50', 'Only Adjusted Top 50', 'Both']
counts = [only_standard, only_adjusted, common]

plt.figure(figsize=(8, 6))
plt.bar(labels, counts, color=['skyblue', 'lightcoral', 'lightgreen'])
plt.ylabel('Number of Philosophers')
plt.title('Overlap of Standard vs Adjusted Centrality Top 50 Lists')
plt.ylim(0, 50) # Y axis range fixed to 0-50

overlap_vis_file = os.path.join(OUTPUT_DIR_VIS, "top50_overlap_analysis.png")
plt.savefig(overlap_vis_file)
print(f"  - Top 50 list overlap visualization saved: {overlap_vis_file}")
plt.close()

# 3. 공통 철학자의 순위 변화 시각화 (산점도)
print("\n--- Generating Rank Comparison Scatter Plot for Common Philosophers ---")

# 두 목록에 모두 포함된 철학자만 필터링
common_philosophers_df = comparison_df[(comparison_df['In_Standard_Top50'] == True) & (comparison_df['In_Adjusted_Top50'] == True)].copy()

# 순위 데이터를 숫자로 변환 (None 값 처리 필요)
common_philosophers_df['Standard_Rank'] = common_philosophers_df['Standard_Rank'].astype(int)
common_philosophers_df['Adjusted_Rank'] = common_philosophers_df['Adjusted_Rank'].astype(int)

plt.figure(figsize=(10, 8))
plt.scatter(common_philosophers_df['Standard_Rank'], common_philosophers_df['Adjusted_Rank'])

# 그래프 범위 설정 (순위이므로 1부터 시작, 50 약간 넘어 여백 확보)
max_rank = 50 # Comparing Top 50, so max rank is 50
plt.xlim(0, max_rank + 5)
plt.ylim(0, max_rank + 5)
plt.gca().invert_yaxis() # Rank is lower for higher importance, invert Y axis
plt.gca().invert_xaxis() # Rank is lower for higher importance, invert X axis

plt.xlabel('Standard Centrality Rank')
plt.ylabel('Adjusted Centrality Rank')
plt.title('Rank Comparison of Common Philosophers in Top 50 Lists')
plt.grid(True)

# 각 점에 철학자 이름 표시 (겹치지 않게 일부만 표시하거나 필요시 주석 처리)
# for i, row in common_philosophers_df.iterrows():
#     plt.annotate(row['Name'], (row['Standard_Rank'], row['Adjusted_Rank']), textcoords="offset points", xytext=(0,5), ha='center')

rank_comparison_vis_file = os.path.join(OUTPUT_DIR_VIS, "top50_rank_comparison_scatter.png")
plt.savefig(rank_comparison_vis_file)
print(f"  - Common philosophers rank comparison visualization saved: {rank_comparison_vis_file}")
plt.close()

print("Script execution completed.") 