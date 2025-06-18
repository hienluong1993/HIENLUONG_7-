import pandas as pd  # 데이터 처리 및 CSV 파일 저장을 위한 라이브러리
from bs4 import BeautifulSoup  # HTML 파싱을 위한 라이브러리
from requests import get  # HTTP 요청을 보내기 위한 라이브러리 url -> 데이터를 가져오려고 사용하는 라이브러리 
import time
from urllib.parse import urljoin
import requests
import random, time



def get_jobkorea_data(corp_name_list, page_no=1):
    """
    JobKorea 웹사이트에서 기업 정보를 크롤링하여 데이터프레임으로 반환하는 함수.
    Args:
        corp_name_list (List[str]): 검색할 기업명 리스트.
        page_no (int): 검색 결과 페이지 번호 (기본값: 1).
    Returns:
        pd.DataFrame: 크롤링된 기업 정보를 포함하는 데이터프레임.
    """
    jobkorea_data = []  # 크롤링된 데이터를 저장할 리스트
    headers = {
        # HTTP 요청에 사용할 User-Agent 헤더 설정 (브라우저처럼 보이게 함)
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    for corp_name in corp_name_list: # 삼성전자
        # 검색 URL 생성 (기업명과 페이지 번호를 포함)
        #       https://www.jobkorea.co.kr/Search?stext=%EC%82%BC%EC%84%B1%EC%A0%84%EC%9E%90&Page_No=4&tabType=corp
        url = f"https://www.jobkorea.co.kr/Search/?stext={corp_name}&tabType=corp&Page_No={page_no}"
        response = get(url, headers=headers)  # HTTP GET 요청을 보내고 응답 받기
        soup = BeautifulSoup(response.text, "html.parser")  # HTML 응답을 파싱

        # Flex 컴포넌트 구조에서 기업 정보를 포함하는 부분 찾기
        #           Flex_display_flex__i0l0hl2 Flex_direction_row__i0l0hl3 Flex_justify_space-between__i0l0hlf
        #           .Flex_display_flex__i0l0hl2 .Flex_direction_row__i0l0hl3 Flex_justify_space-between__i0l0hlf
        flex_containers = soup.find_all(
            "div",
            class_="Flex_display_flex__i0l0hl2 Flex_direction_row__i0l0hl3 Flex_justify_space-between__i0l0hlf",
        )

        
        print(f"Found {len(flex_containers)} flex containers for {corp_name}")
        
        for container in flex_containers: # 10개 중에 1개씩 처리 한다.
            # 내부 Flex 컨테이너 찾기
            #           Flex_display_flex__i0l0hl2 Flex_gap_space12__i0l0hls Flex_direction_row__i0l0hl3
            inner_flex = container.find(
                "div",
                class_="Flex_display_flex__i0l0hl2 Flex_gap_space12__i0l0hls Flex_direction_row__i0l0hl3",
            )
            if not inner_flex:  # 내부 Flex 컨테이너가 없으면 건너뜀
                continue

            # span 태그에서 정보 추출
            spans = inner_flex.find_all(
                "span", class_="Typography_variant_size14__344nw27"
            )
            #print(spans)
            
            if len(spans) >= 3:
                if len(spans) == 3:
                    corp_type = spans[0].get_text(strip=True)
                    corp_location = spans[1].get_text(strip=True)
                    corp_industry = spans[2].get_text(strip=True)
                elif len(spans) == 4:
                    corp_type = spans[1].get_text(strip=True)
                    corp_location = spans[2].get_text(strip=True)
                    corp_industry = spans[3].get_text(strip=True)
            else:
                print(f"정보가 충분하지 않음: {len(spans)} 개의 span 태그 발견")
                continue

            parent = container.find_parent('div', class_="Flex_display_flex__i0l0hl2 Flex_gap_space4__i0l0hly Flex_direction_column__i0l0hl4")
            if not parent:
                print("부모 div를 찾을 수 없습니다.")
                continue

            a_tag = parent.find('a', href=True)
            if not a_tag:
                print("상세 링크를 찾을 수 없습니다.")
                continue
            
            base_url = "https://www.jobkorea.co.kr"

            detail_url = urljoin(base_url, a_tag['href'])
            print("링크:", detail_url)

            capital, sales, ceo, foundation_date = get_detail_data(detail_url, headers)

            jobkorea_data.append({
                "기업명": corp_name,
                "기업형태": corp_type,
                "지역": corp_location,
                "업종": corp_industry,
                "자본금": capital,
                "매출액": sales,
                "대표자": ceo,
                "설립일": foundation_date
            })
            


            time.sleep(random.uniform(2, 5))

    return pd.DataFrame(jobkorea_data)


def get_detail_data(detail_url, headers):
    response = requests.get(detail_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch detail page: {detail_url}")
        return "", "", "", ""

    soup = BeautifulSoup(response.text, "html.parser")

    def get_value(label_text):
        th_tag = soup.find("th", text=label_text)
        if th_tag:
            td_tag = th_tag.find_next("td")
            if td_tag:
                return td_tag.get_text(strip=True)
        return ""

    capital = get_value("자본금")
    sales = get_value("매출액")
    ceo = get_value("대표자")
    foundation_date = get_value("설립일")

    print(f"자본금: {capital}, 매출액: {sales}, 대표자: {ceo}, 설립일: {foundation_date}")
    return capital, sales, ceo, foundation_date

if __name__ == "__main__": 
    """
    메인 실행 코드: 테스트용으로 기업명을 '벡스인텔리전스'로 설정하여 크롤링 수행.
    """
    
    
    df = pd.read_csv("담당_7번.csv")

    corp_name_list = df['기업명'].dropna().unique().tolist()

   
    print(corp_name_list)
   
    test_data = get_jobkorea_data(corp_name_list)

    test_data.to_csv("jobkorea_data_7번.csv", index=False, encoding="utf-8-sig")




    # 결과 출력
    print(test_data.head())
