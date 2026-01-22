import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

options = webdriver.ChromeOptions()
options.add_argument('--blink-settings=imagesEnabled=false') # 속도 향상을 위해 이미지 차단

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

results = []

# [수정] 수집하고 싶은 마지막 페이지 번호를 적어주세요. (예: 100페이지까지)
start_page = 35
end_page = 555

try:
    for page_num in range(start_page, end_page + 1):
        print(f"현재 {page_num}/{end_page} 페이지 수집 중 (50개씩 보기)...")
        
        # 50개씩 보기 파라미터(userDisplay=50) 적용
        url = f"https://cafe.naver.com/cubemania?iframe_url=/ArticleList.nhn%3Fsearch.clubid=10243513%26search.boardtype=L%26search.page={page_num}%26userDisplay=50"
        
        driver.get(url)
        time.sleep(0.1) 
        
        driver.switch_to.frame("cafe_main")
        
        # 게시글 목록 가져오기
        articles = driver.find_elements(By.CSS_SELECTOR, "div.article-board table tbody tr")
        
        # 만약 해당 페이지에 글이 아예 없으면 중단 (데이터가 끝났을 때)
        if not articles:
            print("더 이상 게시글이 없습니다. 수집을 종료합니다.")
            break

        for article in articles:
            try:
                # [공지 필터링] 공지글은 연도와 상관없이 중복되므로 제외 유지
                class_name = article.get_attribute("class")
                if "notice" in class_name:
                    continue 

                num_text = article.find_element(By.CSS_SELECTOR, ".td_article").text
                if "공지" in num_text:
                    continue

                # 데이터 추출 (이제 연도 체크 조건문 없이 무조건 수집합니다)
                title = article.find_element(By.CSS_SELECTOR, "a.article").text
                writer = article.find_element(By.CSS_SELECTOR, "td.td_name").text
                date = article.find_element(By.CSS_SELECTOR, "td.td_date").text
                view = article.find_element(By.CSS_SELECTOR, "td.td_view").text
                
                results.append([title, writer, date, view])
                
            except:
                continue

    # 데이터 정리 및 저장
    df = pd.DataFrame(results, columns=['제목', '작성자', '작성날짜', '조회수'])
    
    # 조회수 숫자로 변환
    df['조회수'] = df['조회수'].astype(str).str.replace(',', '').str.replace('+', '')
    df['조회수'] = pd.to_numeric(df['조회수'], errors='coerce').fillna(0).astype(int)
    
    # 조회수 높은 순으로 정렬
    df = df.sort_values(by='조회수', ascending=False)
    
    df.to_excel("큐브매니아_2025년_대량수집_결과.xlsx", index=False)
    print(f"\n★ 수집 완료! 총 {len(df)}개의 게시글이 저장되었습니다.")

finally:
    driver.quit()