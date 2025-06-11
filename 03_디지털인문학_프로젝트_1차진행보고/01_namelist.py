import requests
from bs4 import BeautifulSoup
import csv
import re

century_urls = {
    "BC": "https://en.wikipedia.org/wiki/List_of_philosophers_born_in_the_centuries_BC",
    "1st–10th": "https://en.wikipedia.org/wiki/List_of_philosophers_born_in_the_1st_through_10th_centuries",
    "11th–14th": "https://en.wikipedia.org/wiki/List_of_philosophers_born_in_the_11th_through_14th_centuries",
    "15th–16th": "https://en.wikipedia.org/wiki/List_of_philosophers_born_in_the_15th_and_16th_centuries",
    "17th": "https://en.wikipedia.org/wiki/List_of_philosophers_born_in_the_17th_century",
    "18th": "https://en.wikipedia.org/wiki/List_of_philosophers_born_in_the_18th_century",
    "19th": "https://en.wikipedia.org/wiki/List_of_philosophers_born_in_the_19th_century",
    "20th": "https://en.wikipedia.org/wiki/List_of_philosophers_born_in_the_20th_century"
}

all_philosophers = []

# 위키피디아 메뉴 링크 패턴
wikipedia_menu_patterns = [
    "Main_Page", "Wikipedia:", "Portal:", "Special:", "Help:", "File:", "Template:", "Category:",
    "Talk:", "User:"
]

for century, url in century_urls.items():
    print(f"Processing {century} century: {url}")
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    
    philosophers_in_century = 0
    
    # 페이지 제목 확인 (실제 철학자 목록 페이지인지)
    page_title = soup.find("h1", {"id": "firstHeading"})
    if page_title and "List of philosophers" in page_title.text:
        # 실제 철학자 정보가 있는 부분 찾기
        main_content = soup.find("div", {"id": "mw-content-text"})
        if main_content:
            # 세기별 섹션 찾기 또는 일반 목록 항목 찾기
            lis = []
            
            # 다양한 구조의 페이지에 맞춰 선택자 적용
            divs = main_content.select("div.div-col, div.column-width, div.columns")
            if divs:
                for div in divs:
                    lis.extend(div.select("li"))
            
            # 다른 형태의 목록 찾기
            if not lis:
                lists = main_content.select("ul")
                for ul in lists:
                    # 탐색 메뉴가 아닌 내용 목록만 포함
                    if not ul.find_parent("div", {"id": "toc"}) and not ul.find_parent("div", {"class": "navbox"}):
                        lis.extend(ul.select("li"))
                        
            for li in lis:
                if not li.text.strip():
                    continue
                
                # 메뉴 항목 제외
                link_tag = li.find("a")
                if link_tag and "href" in link_tag.attrs:
                    # 위키피디아 메뉴 항목 판별
                    href = link_tag["href"]
                    skip = False
                    for pattern in wikipedia_menu_patterns:
                        if pattern in href:
                            skip = True
                            break
                    if skip:
                        continue
                
                try:
                    # 텍스트 파싱
                    text = li.get_text().strip()
                    
                    # 실제 철학자 항목인지 판별 (괄호 안에 년도 정보가 있는지)
                    year_pattern = re.search(r'\(.*?(\d{1,4}(?:–| – | to |–|-)?\d{0,4}).*?\)', text)
                    
                    # 이름과 날짜 파싱
                    if "(" in text and year_pattern:
                        name = text.split('(')[0].strip()
                        date_match = text.split('(')[-1].replace(')', '').strip()
                        
                        # 이름에서 쉼표 제거
                        name = name.replace(",", "").strip()
                        
                        # 너무 짧은 이름 제외 (1-2글자는 아마도 오류)
                        if len(name) <= 2:
                            continue
                            
                        link = "https://en.wikipedia.org" + link_tag["href"] if link_tag and "href" in link_tag.attrs else ""
                        all_philosophers.append([name, date_match, century, link])
                        philosophers_in_century += 1
                
                except Exception as e:
                    print(f"Error processing philosopher: {li.get_text()[:50]}..., Error: {e}")
    
    print(f"Found {philosophers_in_century} philosophers in {century} century")
    
print(f"Total philosophers found: {len(all_philosophers)}")

# CSV 저장
# 파일 경로를 data/raw/ 폴더로 변경
with open("data/raw/philosophers_by_century.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Name", "Date", "Century", "Wikipedia_Link"])
    writer.writerows(all_philosophers)

print("Data saved to data/raw/philosophers_by_century.csv")
