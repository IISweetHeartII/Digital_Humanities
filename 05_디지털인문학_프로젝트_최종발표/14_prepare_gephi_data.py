import pandas as pd
import os

def prepare_gephi_files():
    """
    Gephi 시각화를 위해 상위 50명 철학자 기준으로 노드와 엣지 파일을 생성합니다.
    """
    # 경로 설정 (스크립트의 위치를 기준으로)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, 'data', 'processed')

    try:
        # 1. Top 50 철학자 목록 추출
        top_50_df = pd.read_csv(os.path.join(data_dir, 'top_50_in-degree-centralities_standard.csv'))
        top_50_names = set(top_50_df['Name'].unique())
        print(f"추출된 Top 50 철학자 수: {len(top_50_names)}명")

        # 2. 노드 파일 생성 (nodes_gephi.csv)
        all_nodes_df = pd.read_csv(os.path.join(data_dir, 'centrality_raw.csv'))
        
        # Top 50에 해당하는 노드만 필터링
        gephi_nodes_df = all_nodes_df[all_nodes_df['Name'].isin(top_50_names)].copy()
        
        # Gephi 형식에 맞게 컬럼명 변경 및 추가
        gephi_nodes_df.rename(columns={'Name': 'Id', 'RawCentrality': 'Weight'}, inplace=True)
        gephi_nodes_df['Label'] = gephi_nodes_df['Id']
        
        # 필요한 컬럼만 선택하여 순서 지정
        gephi_nodes_df = gephi_nodes_df[['Id', 'Label', 'Weight']]

        nodes_output_path = os.path.join(data_dir, 'nodes_gephi.csv')
        gephi_nodes_df.to_csv(nodes_output_path, index=False, encoding='utf-8')
        print(f"성공: Gephi 노드 파일 생성 완료 -> {nodes_output_path} ({len(gephi_nodes_df)}개 노드)")


        # 3. 엣지 파일 생성 (edges_gephi.csv)
        all_edges_df = pd.read_csv(os.path.join(data_dir, 'mention_edges.csv'))

        # Source와 Target이 모두 Top 50 목록에 있는 엣지만 필터링
        gephi_edges_df = all_edges_df[
            all_edges_df['Source'].isin(top_50_names) & 
            all_edges_df['Target'].isin(top_50_names)
        ].copy()

        # Weight가 없는 경우 1로 채우기 (기본값)
        if 'Weight' not in gephi_edges_df.columns:
            gephi_edges_df['Weight'] = 1
        else:
            gephi_edges_df['Weight'].fillna(1, inplace=True)

        edges_output_path = os.path.join(data_dir, 'edges_gephi.csv')
        gephi_edges_df.to_csv(edges_output_path, index=False, encoding='utf-8')
        print(f"성공: Gephi 엣지 파일 생성 완료 -> {edges_output_path} ({len(gephi_edges_df)}개 엣지)")

    except FileNotFoundError as e:
        print(f"오류: 파일을 찾을 수 없습니다 - {e}")
    except Exception as e:
        print(f"오류: 데이터 처리 중 예외 발생 - {e}")

if __name__ == '__main__':
    prepare_gephi_files() 