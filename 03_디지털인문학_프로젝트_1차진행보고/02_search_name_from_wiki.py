import pandas as pd
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import time
import random
import os
import glob

# CSV 파일 확인
# 파일 경로를 data/raw/ 폴더로 변경
csv_path = "data/raw/philosophers_by_century.csv"
if not os.path.exists(csv_path):
    print(f"오류: {csv_path} 파일이 존재하지 않습니다.")
    exit(1)

# CSV 파일 읽기
print("철학자 데이터 로딩 중...")
try:
    # 다양한 인코딩 시도
    encodings = ['utf-8', 'cp1252', 'latin1', 'iso-8859-1']
    df = None
    
    for encoding in encodings:
        try:
            df = pd.read_csv(csv_path, encoding=encoding)
            print(f"성공: {encoding} 인코딩으로 파일 로드됨")
            break
        except UnicodeDecodeError:
            continue
    
    if df is None:
        print("오류: 지원되는 인코딩으로 파일을 읽을 수 없습니다")
        exit(1)
    
    names = df["Name"].tolist()
    wiki_links = df["Wikipedia_Link"].tolist()
    print(f"총 {len(names)}명의 철학자 데이터 로드 완료")
except Exception as e:
    print(f"CSV 파일 읽기 오류: {e}")
    exit(1)

# 중복 이름 확인 및 제거
name_set = set()
unique_names = []
unique_links = []

for i, name in enumerate(names):
    if name not in name_set and isinstance(name, str):
        name_set.add(name)
        unique_names.append(name)
        unique_links.append(wiki_links[i])

print(f"중복 제거 후 {len(unique_names)}명의 철학자 데이터 사용")

# 테스트 모드 (주석 처리하여 비활성화)
# test_limit = 10  # 테스트 모드
# unique_names, unique_links = unique_names[:test_limit], unique_links[:test_limit]

# 체크포인트 로딩
start_index = 0
mention_counts = defaultdict(int)
edges = []

# 최신 체크포인트 파일 찾기 (data/checkpoints 폴더 내에서 검색)
checkpoint_files = glob.glob("data/checkpoints/centrality_raw_checkpoint_*.csv")
latest_checkpoint = None
latest_index = 0

for cf in checkpoint_files:
    try:
        # 파일 이름에서 인덱스 추출 (예: centrality_raw_checkpoint_1300.csv)
        index_str = cf.split("_")[-1].split(".")[0]
        index = int(index_str)
        if index > latest_index:
            latest_index = index
            latest_checkpoint = cf
    except:
        continue

if latest_checkpoint:
    print(f"체크포인트 로딩 중: {latest_checkpoint}")
    try:
        # 체크포인트 파일 읽기
        checkpoint_df = pd.read_csv(latest_checkpoint)
        
        # mention_counts 로드
        for index, row in checkpoint_df.iterrows():
            mention_counts[row["Name"]] = row["RawCentrality"]
            
        # 해당 체크포인트까지 처리된 엣지 파일 로드
        edge_checkpoint_file = f"data/checkpoints/mention_edges_checkpoint_{latest_index}.csv"
        if os.path.exists(edge_checkpoint_file):
            edge_df = pd.read_csv(edge_checkpoint_file)
            edges = list(zip(edge_df["Source"], edge_df["Target"]))
            print(f"엣지 데이터 로드 완료: {len(edges)}개")
            
        start_index = latest_index
        print(f"체크포인트 로딩 완료. {start_index}부터 시작합니다.")
        
    except Exception as e:
        print(f"체크포인트 로딩 오류: {e}")
        # 오류 발생 시 처음부터 다시 시작
        start_index = 0
        mention_counts = defaultdict(int)
        edges = []
        print("체크포인트 로딩 실패. 처음부터 다시 시작합니다.")

else:
    print("체크포인트 파일이 없습니다. 처음부터 시작합니다.")


# 언급 횟수 카운트 준비 (체크포인트 로드 후 초기화)
# mention_counts = defaultdict(int) # 이미 위에서 로드 또는 초기화
# edges = [] # 이미 위에서 로드 또는 초기화

# 진행 상황 표시를 위한 변수
total = len(unique_names)
# batch_size = max(1, min(50, (total - start_index) // 20))  # 진행 상황 업데이트 빈도 (남은 항목 기준)
batch_size = 50 # 고정 배치 사이즈로 변경
checkpoint_size = 100  # 중간 결과 저장 주기

print("위키피디아 데이터 수집 시작...")
# 루프를 start_index부터 시작
for i in range(start_index, total):
    source_name = unique_names[i]
    url = unique_links[i]
    
    # 진행 상황 표시
    if (i + 1) % batch_size == 0 or i == total - 1:
        print(f"진행 중: {i+1}/{total} ({(i+1)/total*100:.1f}%)")
    
    # 빈 URL이면 건너뛰기
    if not isinstance(url, str) or not url.startswith("http"):
        print(f"건너뛰기: {source_name} - 유효하지 않은 URL: {url}")
        continue
    
    try:
        # 위키피디아 서버에 과부하 방지를 위한 대기
        time.sleep(random.uniform(0.5, 1.5)) # 대기 시간 조금 늘림
        
        # 페이지 요청
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        res = requests.get(url, headers=headers, timeout=15) # 타임아웃 시간 늘림
        
        # 응답 코드 확인
        if res.status_code != 200:
            print(f"경고: {source_name} 페이지 응답 코드 {res.status_code}")
            continue
            
        # HTML 파싱
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 본문 내용만 추출 (관련 없는 메뉴, 푸터 등 제외)
        main_content = soup.find("div", {"id": "mw-content-text"})
        if main_content:
            text = main_content.get_text().lower()
        else:
            text = soup.get_text().lower()
        
        # 다른 철학자 이름 검색
        mentions_in_page = 0
        for target_name in unique_names:
            # 이름 길이가 너무 짧으면 건너뛰기 (False positive 줄임)
            if len(target_name) <= 2:
                continue
                
            if target_name == source_name:  # 자기 자신은 제외
                continue
                
            # 대소문자 구분 없이 이름 검색
            if isinstance(target_name, str) and target_name.lower() in text:
                mention_counts[target_name] += 1
                edges.append((source_name, target_name))
                mentions_in_page += 1
        
        if mentions_in_page > 0:
            print(f"  - {source_name} 페이지에서 {mentions_in_page}명의 철학자 언급 발견")
                
    except requests.exceptions.Timeout:
        print(f"타임아웃: {source_name}")
    except requests.exceptions.ConnectionError:
        print(f"연결 오류: {source_name}")
        time.sleep(10)  # 연결 오류 시 더 오래 대기
    except Exception as e:
        print(f"오류 발생 ({source_name}): {e}")
    
    # 중간 결과 저장
    # 저장 파일 이름에 현재까지 처리된 총 항목 수를 사용 (i+1)
    if (i + 1) % checkpoint_size == 0 or i == total - 1:
        print(f"중간 결과 저장 중... ({i+1}/{total}개 처리 완료)")
        
        # 중심성 목록 저장 (data/checkpoints 폴더에 저장)
        centrality_list = [{"Name": name, "RawCentrality": mention_counts.get(name, 0)} for name in unique_names]
        centrality_df = pd.DataFrame(centrality_list)
        centrality_df = centrality_df.sort_values(by="RawCentrality", ascending=False)
        centrality_df.to_csv(f"data/checkpoints/centrality_raw_checkpoint_{i+1}.csv", index=False)
        
        # 엣지 리스트 저장 (data/checkpoints 폴더에 저장)
        if edges:
            edges_df = pd.DataFrame(edges, columns=["Source", "Target"])
            # 파일 이름을 현재 인덱스(i+1)로 저장하여 중복 방지 및 순차적 저장
            edges_df.to_csv(f"data/checkpoints/mention_edges_checkpoint_{i+1}.csv", index=False)

print("데이터 수집 완료. 결과 저장 중...")

# 최종 결과 저장 (data/processed 폴더에 저장)
# 중심성 목록 저장
centrality_list = [{"Name": name, "RawCentrality": mention_counts.get(name, 0)} for name in unique_names]
centrality_df = pd.DataFrame(centrality_list)
centrality_df = centrality_df.sort_values(by="RawCentrality", ascending=False)  # 중심성 기준 정렬
centrality_df.to_csv("data/processed/centrality_raw.csv", index=False)
print(f"중심성 데이터 저장 완료: data/processed/centrality_raw.csv (총 {len(centrality_list)}개 항목)")

# 엣지 리스트 저장 (네트워크 구성용)
edges_df = pd.DataFrame(edges, columns=["Source", "Target"])
edges_df.to_csv("data/processed/mention_edges.csv", index=False)
print(f"엣지 데이터 저장 완료: data/processed/mention_edges.csv (총 {len(edges)}개 연결)")

# 상위 중심성 결과 출력
print("\n상위 20명의 언급 횟수:")
for i, row in centrality_df.head(20).iterrows():
    print(f"{row['Name']}: {row['RawCentrality']}회 언급")
