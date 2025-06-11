import pandas as pd
import networkx as nx
import os

# 파일 경로 설정
CENTRALITY_FILE = "data/processed/centrality_raw.csv"
EDGES_FILE = "data/processed/mention_edges.csv"

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
        # print("상위 5개 행:") # 그래프 생성 시 모든 데이터를 사용하므로 생략
        # print(df.head())
        # print("\n결측치 확인:") # 데이터 확인은 verify_data.py에서 수행했으므로 생략
        # print(df.isnull().sum())
        
        return df
    except Exception as e:
        print(f"{file_description} 파일 로딩 오류: {e}")
        return None

# 1. 데이터 파일 로드
centrality_df = load_csv(CENTRALITY_FILE, "중심성 데이터")
edges_df = load_csv(EDGES_FILE, "엣지 데이터")

# 파일 로드 실패 시 종료
if centrality_df is None or edges_df is None:
    print("필요한 데이터 파일 로드에 실패하여 그래프 생성을 중단합니다.")
    exit(1)

# 2. 네트워크 그래프 생성
print("\n--- 네트워크 그래프 생성 중 ---")

# 방향성 그래프 생성
G = nx.DiGraph()

# 노드 추가 (철학자 이름)
# 'Name' 컬럼이 있는지 확인
if "Name" not in centrality_df.columns:
    print("오류: 중심성 파일에 'Name' 컬럼이 없습니다.")
    exit(1)
    
# RawCentrality 값을 노드의 속성으로 추가
for index, row in centrality_df.iterrows():
    name = row["Name"]
    raw_centrality = row["RawCentrality"]
    if pd.notna(name):
        G.add_node(name, raw_centrality=raw_centrality)

print(f"그래프에 {G.number_of_nodes()}개의 노드 추가 완료")

# 엣지 추가 (언급 관계)
# 'Source'와 'Target' 컬럼이 있는지 확인
if "Source" not in edges_df.columns or "Target" not in edges_df.columns:
    print("오류: 엣지 파일에 'Source' 또는 'Target' 컬럼이 없습니다.")
    exit(1)
    
# 엣지 데이터프레임을 엣지 리스트로 변환하여 추가 (결측치 제거)
edges = edges_df.dropna(subset=["Source", "Target"])

# NetworkX의 from_pandas_edgelist 함수 사용
# source, target 컬럼 지정
nx.from_pandas_edgelist(edges, source='Source', target='Target', create_using=G)
print(f"그래프에 {G.number_of_edges()}개의 엣지 추가 완료")

# 3. 그래프 정보 출력
print("\n--- 생성된 그래프 정보 ---")
print(f"그래프 유형: {type(G)}")
print(f"노드 수: {G.number_of_nodes()}")
print(f"엣지 수: {G.number_of_edges()}")

# 그래프 객체를 추후 분석에 사용하기 위해 저장하거나 유지할 수 있습니다.
# 여기서는 객체를 생성하는 것까지만 수행합니다.

print("네트워크 그래프 생성 완료.") 