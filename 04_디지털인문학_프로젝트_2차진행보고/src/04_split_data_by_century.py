import pandas as pd
import os

# 파일 경로 설정
PHILOSOPHERS_FILE = "data/raw/philosophers_by_century.csv"
OUTPUT_DIR = "data/processed/by_century/"

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

# 1. 철학자 목록 파일 로드
philosophers_df = load_csv(PHILOSOPHERS_FILE, "철학자 목록")

# 파일 로드 실패 시 종료
if philosophers_df is None:
    print("철학자 목록 파일 로드에 실패하여 스크립트를 종료합니다.")
    exit(1)

# 'Century' 컬럼이 있는지 확인
if "Century" not in philosophers_df.columns:
    print("오류: 철학자 목록 파일에 'Century' 컬럼이 없습니다. 스크립트를 종료합니다.")
    exit(1)

# 2. 고유한 세기 목록 확인
centuries = philosophers_df["Century"].unique()
print(f"\n--- 확인된 고유 세기 목록: {list(centuries)} ---")

# 3. 세기별 데이터 분리 및 저장
print(f"\n--- 세기별 데이터 분리 및 {OUTPUT_DIR}에 저장 중 ---")

# 출력 디렉토리 생성 (이미 위에서 생성했지만, 스크립트 단독 실행을 위해 다시 확인)
os.makedirs(OUTPUT_DIR, exist_ok=True)

processed_centuries = 0

for century in centuries:
    # 유효한 세기 이름인지 확인 (NaN 값 등 제외)
    if pd.isna(century):
        print("경고: 유효하지 않은 세기 값(NaN)이 발견되었습니다. 해당 데이터는 건너뜁니다.")
        continue
        
    print(f"  - '{century}' 세기 데이터 처리 중...")
    
    # 해당 세기의 데이터 필터링
    century_df = philosophers_df[philosophers_df["Century"] == century].copy()
    
    # 파일 이름에 사용할 수 있도록 세기 이름 정리 (예: '1st–10th' -> '1st_10th')
    # 파일 시스템에서 문제될 수 있는 문자 제거 또는 변경
    safe_century_name = str(century).replace(" ", "_").replace("–", "-").replace("/", "_").replace("\\", "_").replace(":", "_").replace("*", "_").replace("?", "_").replace("\"", "_").replace("<", "_").replace(">", "_").replace("|", "_")
    
    # 파일 경로 설정
    output_filepath = os.path.join(OUTPUT_DIR, f"philosophers_{safe_century_name}.csv")
    
    # CSV 파일로 저장
    try:
        century_df.to_csv(output_filepath, index=False, encoding='utf-8')
        print(f"    - 저장 완료: {output_filepath} ({len(century_df)}개 항목)")
        processed_centuries += 1
    except Exception as e:
        print(f"    - 오류: '{century}' 세기 데이터 저장 중 오류 발생 - {e}")

print(f"\n--- 총 {processed_centuries}개의 세기별 파일 저장 완료 ---")
print(f"결과 파일은 '{OUTPUT_DIR}' 폴더에서 확인 가능합니다.") 