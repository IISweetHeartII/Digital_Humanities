"""
영화 데이터를 감독-배우 네트워크 분석용 Gephi 데이터로 변환
"""
import pandas as pd
import ast
from pathlib import Path

class DirectorActorPreprocessor:
    def __init__(self, input_file='data/raw/movie_data.csv'):
        """
        초기화 함수
        
        Args:
            input_file (str): 입력 CSV 파일 경로
        """
        self.input_file = input_file
        self.output_dir = Path('data/gephi')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.actor_id_map = {}  # 배우 이름을 고유 ID로 매핑
        self.director_id_map = {}  # 감독 이름을 고유 ID로 매핑
        
    def generate_unique_id(self, name, role, count=1):
        """
        이름에 대한 고유 ID 생성
        
        Args:
            name (str): 이름
            role (str): 'Actor' 또는 'Director'
            count (int): 동명이인 구분용 카운터
        """
        # 한글 이름을 그대로 사용
        base_id = f"{name.strip()}_{role[:3]}_{count}"
        return base_id
        
    def load_and_filter_data(self):
        """
        데이터 로드 및 필터링
        - 2021-2024년 데이터
        - 출연 배우 3명 이상
        - 감독당 최소 2편 이상
        """
        # 데이터 로드 시 인코딩 지정
        df = pd.read_csv(self.input_file, encoding='utf-8')
        
        # 문자열 리스트를 실제 리스트로 변환
        df['actors'] = df['actors'].apply(ast.literal_eval)
        df['genre'] = df['genre'].apply(ast.literal_eval)
        
        # 2021년 이후 데이터만 필터링
        df['production_year'] = pd.to_numeric(df['production_year'], errors='coerce')
        df = df[df['production_year'] >= 2021]
        
        # 배우가 3명 이상인 영화만 선택
        df['actor_count'] = df['actors'].apply(len)
        df = df[df['actor_count'] >= 3]
        
        # 감독별 영화 수 계산
        director_counts = df['director'].value_counts()
        directors_with_multiple_films = director_counts[director_counts >= 2].index
        
        # 2편 이상 연출한 감독의 영화만 선택
        df = df[df['director'].isin(directors_with_multiple_films)]
        
        # 감독 이름 정규화 및 ID 매핑 생성
        for director in df['director'].unique():
            if director not in self.director_id_map:
                self.director_id_map[director] = self.generate_unique_id(director, 'Director')
        
        # 배우 이름 정규화 및 ID 매핑 생성
        actor_counts = {}
        for actors in df['actors']:
            for actor in actors:
                actor = actor.strip()
                if actor not in actor_counts:
                    actor_counts[actor] = 1
                    self.actor_id_map[actor] = self.generate_unique_id(actor, 'Actor')
                elif actor not in self.actor_id_map:
                    actor_counts[actor] += 1
                    self.actor_id_map[actor] = self.generate_unique_id(actor, 'Actor', actor_counts[actor])
        
        self.data = df
        print(f"필터링 후 영화 수: {len(df)}")
        
    def create_nodes(self):
        """
        노드(감독, 배우) 데이터 생성
        """
        # 감독 노드
        directors = pd.DataFrame({
            'Id': [self.director_id_map[d] for d in self.data['director'].unique()],
            'Label': self.data['director'].unique(),
            'Type': 'Director',
            'MovieCount': self.data['director'].value_counts()
        })
        
        # 배우 노드
        actors = set()
        actor_movies = {}
        actor_genres = {}
        
        for _, row in self.data.iterrows():
            for actor in row['actors']:
                actor = actor.strip()
                actors.add(actor)
                actor_movies[actor] = actor_movies.get(actor, 0) + 1
                if actor not in actor_genres:
                    actor_genres[actor] = set()
                actor_genres[actor].update(row['genre'])
        
        actors = pd.DataFrame({
            'Id': [self.actor_id_map[a] for a in actors],
            'Label': list(actors),
            'Type': 'Actor',
            'MovieCount': [actor_movies[a] for a in actors],
            'Genres': [list(actor_genres[a]) for a in actors]
        })
        
        # 노드 통합
        self.nodes = pd.concat([directors, actors], ignore_index=True)
        print(f"총 노드 수: {len(self.nodes)} (감독: {len(directors)}, 배우: {len(actors)})")
        
    def create_edges(self):
        """
        엣지(감독-배우 협업) 데이터 생성
        """
        edges = []
        for _, row in self.data.iterrows():
            director = row['director']
            director_id = self.director_id_map[director]
            for actor in row['actors']:
                actor = actor.strip()
                actor_id = self.actor_id_map[actor]
                edges.append({
                    'Source': director_id,
                    'Target': actor_id,
                    'Type': 'Undirected',
                    'Weight': 1
                })
        
        # 엣지 통합 및 가중치 계산
        self.edges = pd.DataFrame(edges)
        self.edges = self.edges.groupby(['Source', 'Target', 'Type'], as_index=False)['Weight'].sum()
        print(f"총 엣지 수: {len(self.edges)}")
        
    def save_gephi_files(self):
        """
        Gephi 포맷으로 파일 저장
        """
        # UTF-8 with BOM으로 저장
        self.nodes.to_csv(self.output_dir / 'nodes.csv', index=False, encoding='utf-8-sig')
        self.edges.to_csv(self.output_dir / 'edges.csv', index=False, encoding='utf-8-sig')
        print(f"파일 저장 완료: {self.output_dir}")

def main():
    """
    메인 실행 함수
    """
    preprocessor = DirectorActorPreprocessor()
    preprocessor.load_and_filter_data()
    preprocessor.create_nodes()
    preprocessor.create_edges()
    preprocessor.save_gephi_files()

if __name__ == '__main__':
    main()