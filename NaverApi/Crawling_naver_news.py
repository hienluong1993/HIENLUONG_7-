# curl "https://openapi.naver.com/v1/search/news.xml?query=%EC%A3%BC%EC%8B%9D&display=10&start=1&sort=sim" \
# -H "X-Naver-Client-Id: {애플리케이션 등록 시 발급받은 클라이언트 아이디 값}" \
# -H "X-Naver-Client-Secret: {애플리케이션 등록 시 발급받은 클라이언트 시크릿 값}" -v

# Naver News API 발급 주소
# 1일 25,000건 제한
# https://developers.naver.com/main/

# Documentation: https://developers.naver.com/docs/serviceapi/search/news/news.md#%EB%89%B4%EC%8A%A4
# 네이버 API 신청 현황 : https://developers.naver.com/apps/#/list


# 클라이언트 아이디 값
# 64g43aYmdLhFMenUVVVZ

# 클라이언트 시크릿 값
# LrXCNWZHsp

# 요청 코드 예시
# curl "https://openapi.naver.com/v1/search/news.json?query=LG&display=10&start=1&sort=sim" -H "X-Naver-Client-Id: CFN_cKg1htsqD1xqkA0k" -H "X-Naver-Client-Secret: 52E_v8ylTA" -v

# curl https://openapi.naver.com/v1/search/news.json?query=%EC%A3%BC%EC%8B%9D&display=10&start=1&sort=sim \
#     -H "X-Naver-Client-Id: CFN_cKg1htsqD1xqkA0k" \
#     -H "X-Naver-Client-Secret: 52E_v8ylTA" -v

# Python 코드로 네이버 뉴스 API 호출 구현
import requests
import urllib.parse
import json
import os
import re
from datetime import datetime
import pandas as pd


# API 키 설정
client_id = "85EpIzMV_0b7cGFe4eA5"
client_secret = "LcLRv7meUk"

# 검색어 설정 및 인코딩 (500 회사)
company_csv = "담당_7번.csv"
df_companies = pd.read_csv(company_csv)
company_list = df_companies["기업명"].dropna().unique().tolist()

# API URL 설정 (JSON 형식) 및 헤더 설정
def fetch_news(company_name, display=10):
    encoded_query = urllib.parse.quote(company_name)
    url = f"https://openapi.naver.com/v1/search/news.json?query={encoded_query}&display={display}&start=1&sort=sim"

    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
        "User-Agent": "Mozilla/5.0",
    }
    # 디버깅용 헤더 출력
    print(f"Using headers: {headers}")
    
# API 요청 보내기
    try:
        response = requests.get(url, headers=headers)
        print(f"[{company_name}] Response Status: {response.status_code}")
        print(f"[{company_name}] Response headers: {response.headers}")
        # 응답 확인
        if response.status_code == 200:
            # JSON 결과 파싱
            data = json.loads(response.text)
            news_items = data.get("items", [])
            print(f"총 검색 결과: {data['total']}개")
            
            # 검색 결과 출력
            for idx, item in enumerate(news_items, 1):
                print(f"\n[{idx}] {re.sub(r'<.*?>', '', item['title'])}")
                print(f"링크: {item['link']}")
                print(f"설명: {re.sub(r'<.*?>', '', item['description'])}")
                print(f"발행일: {item['pubDate']}")

            # 태그 제거 + 회사 정보 추가
            for item in news_items:
                item["company"] = company_name
                item["title"] = re.sub(r"<.*?>", "", item["title"])
                item["description"] = re.sub(r"<.*?>", "", item["description"])
                item["originallink"] = item.get("originallink", "")
            return news_items
        else:
            print(f"Error: {response.status_code} for {company_name}")
            print(f"Response body: {response.text}")
            return []
    except Exception as e:
        print(f"Exception with {company_name}: {e}")
        return []

all_news = []
for idx, company in enumerate(company_list, 1):
    print(f"[{idx}/{len(company_list)}] Fetching: {company}")
    news = fetch_news(company)
    all_news.extend(news)

#   검색 결과 데이터프레임으로 변환
if all_news:
    df_news = pd.DataFrame(all_news)
    # HTML 태그 제거 및 텍스트 정리
    if "title" in df_news.columns:
        # 모든 HTML 태그를 정규식으로 제거
        df_news["title"] = df_news["title"].apply(lambda x: re.sub(r"<.*?>", "", x))
        df_news["description"] = df_news["description"].apply(lambda x: re.sub(r"<.*?>", "", x))

     # 현재 시간을 파일명에 추가하여 저장
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"Crawling_Naver_news_data_7번{current_time}.csv"

    # os.path를 사용하여 경로 생성
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(output_dir, file_name)
   
    df_news.to_csv(file_name, index=False, encoding="utf-8-sig")
    print(f"\n데이터가 저장되었습니다: {file_name}")
else:
    print("데이터가 없습니다.")
    
# XML 형식으로 요청하려면 아래 URL을 사용
# url = f"https://openapi.naver.com/v1/search/news.xml?query={encoded_query}&display=10&start=1&sort=sim"


