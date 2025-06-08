import os
import json
import time
from datetime import datetime, timedelta
import requests # type: ignore
import pandas as pd
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class KobisDataCollector:
    """KOBIS Open API를 사용하여 영화 데이터를 수집하는 클래스"""
    
    def __init__(self, api_key):
        """
        Args:
            api_key (str): KOBIS Open API 키
        """
        self.api_key = api_key
        self.base_url = "http://www.kobis.or.kr/kobisopenapi/webservice/rest"
        
    def get_movie_list(self, start_date, end_date):
        """특정 기간 동안의 영화 목록을 조회
        
        Args:
            start_date (str): 시작일 (YYYYMMDD)
            end_date (str): 종료일 (YYYYMMDD)
            
        Returns:
            list: 영화 정보 목록
        """
        endpoint = f"{self.base_url}/movie/searchMovieList.json"
        movies = []
        cur_page = 1
        
        while True:
            params = {
                'key': self.api_key,
                'openStartDt': start_date[:4],  # 개봉연도 시작
                'openEndDt': end_date[:4],      # 개봉연도 끝
                'itemPerPage': 100,
                'curPage': cur_page,
                'repNationCd': '22041011'  # 한국 영화 코드
            }
            
            try:
                response = requests.get(endpoint, params=params)
                data = response.json()
                movie_list = data['movieListResult']['movieList']
                
                if not movie_list:  # 더 이상 데이터가 없으면 종료
                    break
                    
                movies.extend(movie_list)
                cur_page += 1
                time.sleep(0.2)  # API 호출 간격 조절
                
            except Exception as e:
                print(f"영화 목록 조회 중 오류 발생 (페이지: {cur_page}): {e}")
                break
        
        return movies

    def get_movie_info(self, movie_cd):
        """영화 상세 정보 조회
        
        Args:
            movie_cd (str): 영화 코드
            
        Returns:
            dict: 영화 상세 정보
        """
        endpoint = f"{self.base_url}/movie/searchMovieInfo.json"
        params = {
            'key': self.api_key,
            'movieCd': movie_cd
        }
        
        try:
            response = requests.get(endpoint, params=params)
            data = response.json()
            return data['movieInfoResult']['movieInfo']
        except Exception as e:
            print(f"영화 상세 정보 조회 중 오류 발생 (영화코드: {movie_cd}): {e}")
            return None

    def collect_movie_data(self, start_date, end_date):
        """영화 데이터 수집 및 DataFrame 생성
        
        Args:
            start_date (str): 시작일 (YYYYMMDD)
            end_date (str): 종료일 (YYYYMMDD)
            
        Returns:
            pd.DataFrame: 수집된 영화 데이터
        """
        movies = []
        movie_list = self.get_movie_list(start_date, end_date)
        total_movies = len(movie_list)
        
        print(f"총 {total_movies}개의 영화 데이터 수집 시작...")
        
        for idx, movie in enumerate(movie_list, 1):
            print(f"처리 중: {idx}/{total_movies} - {movie['movieNm']}")
            
            movie_info = self.get_movie_info(movie['movieCd'])
            if movie_info:
                # 감독 정보 추출
                directors = movie_info.get('directors', [])
                director_name = directors[0]['peopleNm'] if directors else '정보없음'
                
                # 배우 정보 추출 (모든 배우 포함)
                actors = movie_info.get('actors', [])
                actor_names = [actor['peopleNm'] for actor in actors]
                
                # 장르 정보 추출
                genres = movie_info.get('genres', [])
                genre_names = [genre['genreNm'] for genre in genres]
                
                movies.append({
                    'movie_cd': movie_info['movieCd'],
                    'title': movie_info['movieNm'],
                    'director': director_name,
                    'actors': actor_names,
                    'actor_count': len(actor_names),
                    'release_date': movie_info.get('openDt', ''),
                    'genre': genre_names,
                    'genre_count': len(genre_names),
                    'production_year': movie_info.get('prdtYear', ''),
                    'show_time': movie_info.get('showTm', '')
                })
                
                time.sleep(0.2)  # API 호출 간격 조절
        
        return pd.DataFrame(movies)

    def save_to_csv(self, df, output_path):
        """데이터프레임을 CSV 파일로 저장
        
        Args:
            df (pd.DataFrame): 저장할 데이터프레임
            output_path (str): 저장 경로
        """
        # 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"데이터가 {output_path}에 저장되었습니다.")

def main():
    """메인 실행 함수"""
    # API 키는 환경 변수에서 가져오기
    api_key = os.getenv('KOBIS_API_KEY')
    if not api_key:
        raise ValueError("KOBIS_API_KEY 환경 변수가 설정되지 않았습니다.")
    
    # 데이터 수집기 초기화
    collector = KobisDataCollector(api_key)
    
    # 2019-2024년 데이터 수집
    start_date = "20190101"
    end_date = "20241231"
    
    # 데이터 수집 및 저장
    df = collector.collect_movie_data(start_date, end_date)
    collector.save_to_csv(df, 'data/raw/movie_data.csv')
    
    # 수집 결과 요약 출력
    print("\n=== 데이터 수집 결과 ===")
    print(f"총 영화 수: {len(df)}")
    print(f"총 감독 수: {df['director'].nunique()}")
    print(f"총 배우 수: {sum([len(actors) for actors in df['actors']])}")
    print(f"평균 배우 수: {df['actor_count'].mean():.1f}")
    print(f"장르 분포:\n{df['genre'].explode().value_counts().head()}")

if __name__ == "__main__":
    main() 