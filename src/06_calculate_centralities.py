import pandas as pd
import networkx as nx
import os

# 파일 경로 설정
CENTRALITY_RAW_FILE = "data/processed/centrality_raw.csv"
EDGES_FILE = "data/processed/mention_edges.csv"
OUTPUT_FILE = "data/processed/centralities.csv"

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

# 1. 데이터 파일 로드 및 그래프 생성 (src/05_create_network_graph.py 로직 포함)
print("--- 데이터 로드 및 네트워크 그래프 생성 중 ---")
centrality_df = load_csv(CENTRALITY_RAW_FILE, "중심성 원본 데이터")
edges_df = load_csv(EDGES_FILE, "엣지 데이터")

# 파일 로드 실패 시 종료
if centrality_df is None or edges_df is None:
    print("필요한 데이터 파일 로드에 실패하여 중심성 계산을 중단합니다.")
    exit(1)

# 방향성 그래프 생성
G = nx.DiGraph()

# 노드 추가 (철학자 이름)
if "Name" not in centrality_df.columns:
    print("오류: 중심성 원본 파일에 'Name' 컬럼이 없습니다.")
    exit(1)
    
# RawCentrality 값을 노드의 속성으로 추가
for index, row in centrality_df.iterrows():
    name = row["Name"]
    raw_centrality = row["RawCentrality"]
    if pd.notna(name):
        G.add_node(name, raw_centrality=raw_centrality)

print(f"그래프에 {G.number_of_nodes()}개의 노드 추가 완료")

# 엣지 추가 (언급 관계)
if "Source" not in edges_df.columns or "Target" not in edges_df.columns:
    print("오류: 엣지 파일에 'Source' 또는 'Target' 컬럼이 없습니다.")
    exit(1)
    
edges = edges_df.dropna(subset=["Source", "Target"])

# NetworkX의 from_pandas_edgelist 함수 사용
nx.from_pandas_edgelist(edges, source='Source', target='Target', create_using=G)
print(f"그래프에 {G.number_of_edges()}개의 엣지 추가 완료")

print("네트워크 그래프 생성 완료.")

# 2. 중심성 지표 계산
print("\n--- 중심성 지표 계산 중 ---")

# In-Degree Centrality 계산 (다른 노드로부터 받은 연결 수)
in_degree_centrality = nx.in_degree_centrality(G)
print("In-Degree Centrality 계산 완료")

# Out-Degree Centrality 계산 (다른 노드에게 보낸 연결 수)
out_degree_centrality = nx.out_degree_centrality(G)
print("Out-Degree Centrality 계산 완료")

# Closeness Centrality 계산
# 연결되지 않은 그래프의 경우 에러 발생 가능 -> subgraphs 확인 또는 연결 요소별 계산 필요
# 여기서는 간단하게 처리하며, 필요시 예외 처리 또는 연결된 컴포넌트만 계산
try:
    closeness_centrality = nx.closeness_centrality(G)
    print("Closeness Centrality 계산 완료")
except nx.NetworkXPointlessConcept:
    print("경고: 그래프가 연결되어 있지 않아 Closeness Centrality를 계산할 수 없습니다.")
    closeness_centrality = {node: 0 for node in G.nodes()}

# Betweenness Centrality 계산
# k를 설정하여 근사 계산 (대규모 그래프에 적합)
# k=None 또는 모든 노드를 사용하면 정확하지만 오래 걸림
# 여기서는 모든 노드로 계산 (작은 규모의 그래프라고 가정)
# 만약 느리면 k 값을 설정하여 근사 계산으로 변경할 수 있습니다.
print("Betweenness Centrality 계산 중... (시간 소요될 수 있음)")
betweenness_centrality = nx.betweenness_centrality(G, k=None, normalized=True, endpoints=False)
print("Betweenness Centrality 계산 완료")

# Eigenvector Centrality 계산
# 수렴하지 않을 경우 에러 발생 가능 -> max_iter 증가 또는 tol 조정 필요
# 여기서는 기본 설정 사용
try:
    eigenvector_centrality = nx.eigenvector_centrality(G)
    print("Eigenvector Centrality 계산 완료")
except nx.PowerIterationFailedConvergence:
    print("경고: Eigenvector Centrality 계산이 수렴하지 않았습니다. 결과를 신뢰할 수 없습니다.")
    eigenvector_centrality = {node: 0 for node in G.nodes()}

print("중심성 지표 계산 완료.")

# 3. 결과 정리 및 저장
print("\n--- 결과 정리 및 저장 중 ---")

# 결과를 DataFrame으로 변환
centrality_results = pd.DataFrame({
    'Name': list(G.nodes()),
    'In-Degree Centrality': [in_degree_centrality.get(node, 0) for node in G.nodes()],
    'Out-Degree Centrality': [out_degree_centrality.get(node, 0) for node in G.nodes()],
    'Closeness Centrality': [closeness_centrality.get(node, 0) for node in G.nodes()],
    'Betweenness Centrality': [betweenness_centrality.get(node, 0) for node in G.nodes()],
    'Eigenvector Centrality': [eigenvector_centrality.get(node, 0) for node in G.nodes()]
})

# RawCentrality 값도 DataFrame에 추가
# 노드 속성에서 가져오기
raw_centrality_values = {node: G.nodes[node].get('raw_centrality', 0) for node in G.nodes()}
centrality_results['RawCentrality'] = centrality_results['Name'].map(raw_centrality_values)

# In-Degree Centrality가 RawCentrality와 일치하는지 확인 (방향 그래프의 In-Degree는 외부로부터의 링크 수)
# NetworkX의 in_degree_centrality는 정규화된 값임. 정규화되지 않은 in_degree는 G.in_degree()로 얻을 수 있음.
# RawCentrality는 정규화되지 않은 값이므로 G.in_degree()와 비교하는 것이 맞음.

# 정규화되지 않은 In-Degree 계산
in_degree_counts = dict(G.in_degree())

# RawCentrality와 정규화되지 않은 In-Degree Count 비교
# RawCentrality 컬럼은 원래 데이터에서 가져온 것이므로, 계산된 In-Degree Count와 비교하여 일관성을 확인
# centrality_results DataFrame에 RawCentrality 컬럼이 이미 있으므로, 계산된 In-Degree count를 추가하여 비교
centrality_results['Calculated_In_Degree_Count'] = centrality_results['Name'].map(in_degree_counts)

# 필요하다면 RawCentrality와 Calculated_In_Degree_Count가 일치하는지 검증 로직 추가 가능
# 예: assert (centrality_results['RawCentrality'] == centrality_results['Calculated_In_Degree_Count']).all()

# 결과 파일을 data/processed/ 폴더에 저장
centrality_results.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')

print(f"중심성 계산 결과 저장 완료: {OUTPUT_FILE} ({len(centrality_results)}개 항목)")

print("스크립트 실행 완료.") 