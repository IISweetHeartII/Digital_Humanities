import pandas as pd
import os

# 파일 경로 설정
PHILOSOPHERS_FILE = "data/raw/philosophers_by_century.csv"
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
        print("상위 5개 행:")
        print(df.head())
        print("\n결측치 확인:")
        print(df.isnull().sum())
        
        return df
    except Exception as e:
        print(f"{file_description} 파일 로딩 오류: {e}")
        return None

# 1. 파일 로드
philosophers_df = load_csv(PHILOSOPHERS_FILE, "철학자 목록")
centrality_df = load_csv(CENTRALITY_FILE, "중심성 데이터")
edges_df = load_csv(EDGES_FILE, "엣지 데이터")

# 파일 로드 실패 시 종료
if philosophers_df is None or centrality_df is None or edges_df is None:
    print("필요한 파일 로드에 실패하여 데이터 확인을 중단합니다.")
    exit(1)

# 2. 데이터 일관성 확인
print("\n--- 데이터 일관성 확인 중 ---")

# 철학자 목록에서 고유한 이름 추출
# 이름 컬럼이 있는지 확인하고 없는 경우 오류 메시지 출력 후 종료
if "Name" not in philosophers_df.columns:
    print(f"오류: 철학자 목록 파일에 'Name' 컬럼이 없습니다.")
    exit(1)
    
unique_philosophers = set(philosophers_df["Name"].dropna().tolist())
print(f"철학자 목록 파일의 고유 이름 수: {len(unique_philosophers)}")

# 중심성 데이터 확인
if "Name" not in centrality_df.columns or "RawCentrality" not in centrality_df.columns:
     print(f"오류: 중심성 데이터 파일에 'Name' 또는 'RawCentrality' 컬럼이 없습니다.")
     exit(1)
     
centrality_names = set(centrality_df["Name"].dropna().tolist())
print(f"중심성 데이터 파일의 이름 수: {len(centrality_names)}")

# 엣지 데이터 확인
if "Source" not in edges_df.columns or "Target" not in edges_df.columns:
     print(f"오류: 엣지 데이터 파일에 'Source' 또는 'Target' 컬럼이 없습니다.")
     exit(1)

edge_names = set(edges_df["Source"].dropna().tolist() + edges_df["Target"].dropna().tolist())
print(f"엣지 데이터 파일에 언급된 고유 이름 수: {len(edge_names)}")

# 중심성 데이터의 모든 이름이 철학자 목록에 있는지 확인
missing_in_philosophers_from_centrality = centrality_names - unique_philosophers
if missing_in_philosophers_from_centrality:
    print(f"경고: 중심성 데이터에 있지만 철학자 목록에 없는 이름 {len(missing_in_philosophers_from_centrality)}개 발견:")
    # 처음 10개만 출력
    for name in list(missing_in_philosophers_from_centrality)[:10]:
        print(f"  - {name}")
    if len(missing_in_philosophers_from_centrality) > 10:
        print("  ...")
else:
    print("중심성 데이터의 모든 이름이 철학자 목록에 있습니다.")

# 엣지 데이터의 모든 이름이 철학자 목록에 있는지 확인
missing_in_philosophers_from_edges = edge_names - unique_philosophers
if missing_in_philosophers_from_edges:
    print(f"경고: 엣지 데이터에 언급되었지만 철학자 목록에 없는 이름 {len(missing_in_philosophers_from_edges)}개 발견:")
    # 처음 10개만 출력
    for name in list(missing_in_philosophers_from_edges)[:10]:
        print(f"  - {name}")
    if len(missing_in_philosophers_from_edges) > 10:
        print("  ...")
else:
    print("엣지 데이터의 모든 이름이 철학자 목록에 있습니다.")

# 3. 간단한 데이터 유효성 검사
print("\n--- 간단한 데이터 유효성 검사 중 ---")

# RawCentrality 값이 음수인지 확인 (음수일 수 없음)
if (centrality_df["RawCentrality"] < 0).any():
    print("경고: RawCentrality 값 중 음수가 발견되었습니다.")
else:
    print("RawCentrality 값에 음수가 없습니다.")

# Wikipedia_Link가 유효한 URL 형식인지 (간단히 http/https 시작 확인)
if "Wikipedia_Link" in philosophers_df.columns:
    invalid_links = philosophers_df[~philosophers_df["Wikipedia_Link"].astype(str).str.startswith(('http://', 'https://')) & philosophers_df["Wikipedia_Link"].notna()]
    if not invalid_links.empty:
        print(f"경고: 유효하지 않은 Wikipedia_Link 형식 {len(invalid_links)}개 발견:")
        # 처음 5개만 출력
        for index, row in invalid_links.head().iterrows():
            print(f"  - 이름: {row['Name']}, 링크: {row['Wikipedia_Link']}")
        if len(invalid_links) > 5:
            print("  ...")
    else:
        print("Wikipedia_Link 형식이 유효합니다.")
else:
    print("Wikipedia_Link 컬럼이 없습니다.")

print("\n데이터 확인 완료.")
print("보고서 작성 가이드라인에 따라 추가적인 심층 분석 및 검증을 진행할 수 있습니다.") 