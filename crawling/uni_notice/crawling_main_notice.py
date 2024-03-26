from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup
import json
import requests
from bs4 import BeautifulSoup
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import hashlib
import json
import os
import time
from dotenv import load_dotenv
# Firebase 초기 설정
def initial_setting():
    load_dotenv()
    cred = credentials.Certificate('./firebase_admin_key.json')
    firebase_database_url = "https://mypknu-default-rtdb.asia-southeast1.firebasedatabase.app/"
    firebase_admin.initialize_app(cred, {
        'databaseURL': firebase_database_url    })

# 공지사항 데이터로부터 해시값 생성
def generate_hash(notice):
    notice_str = f"{notice['title']}{notice['user']}{notice['date']}"
    return hashlib.sha256(notice_str.encode()).hexdigest()

# 데이터베이스에서 현재 저장된 모든 공지사항의 해시값을 가져옴
def get_existing_hashes():
    metadata_ref = db.reference('/notices_metadata')
    return set(metadata_ref.get().keys()) if metadata_ref.get() else set()

# 데이터베이스에 공지사항 추가 또는 업데이트
def update_notice(notice, notice_hash):
    notices_ref = db.reference('/notices')
    metadata_ref = db.reference('/notices_metadata')
    notices_ref.child(notice_hash).set(notice)
    metadata_ref.child(notice_hash).set({'date': notice['date']})
    print(f"Added or updated notice: {notice['number']} - {notice['title']}")

# 데이터베이스에서 공지사항 삭제
def remove_notice(hash_to_remove):
    notices_ref = db.reference('/notices')
    metadata_ref = db.reference('/notices_metadata')
    notice_to_remove = notices_ref.child(hash_to_remove).get()
    notices_ref.child(hash_to_remove).delete()
    metadata_ref.child(hash_to_remove).delete()
    print(f"Removed notice: {notice_to_remove['number']} - {notice_to_remove['title']}")

# 공지사항 데이터 처리
def process_notices(notices, insert_to_firebase):
    if insert_to_firebase:
        existing_hashes = get_existing_hashes()
        initial_count = len(existing_hashes)
        print(f"Initial number of notices: {initial_count}")
        update_count = 0
        remove_count = 0
        new_hashes = {generate_hash(notice) for notice in notices}
        to_update = new_hashes - existing_hashes
        to_remove = existing_hashes - new_hashes
        for notice in notices:
            notice_hash = generate_hash(notice)
            if notice_hash in to_update:
                update_notice(notice, notice_hash)
                update_count += 1
        for hash_to_remove in to_remove:
            remove_notice(hash_to_remove)
            remove_count += 1
        final_count = initial_count - remove_count + update_count
        print(f"Updated notices: {update_count}")
        print(f"Removed notices: {remove_count}")
        print(f"Final number of notices: {final_count}")
        print("Database update complete.")
    else:
        print("Notices crawled but not inserted into Firebase.")

def main_crawling(url, cd_num):
    notices = []
    response = requests.get(url, verify=False)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    for tr in soup.find_all('tr', class_=lambda x: x != 'noti'):
        title_tag = tr.find('td', class_='bdlTitle')
        user_tag = tr.find('td', class_='bdlUser')
        date_tag = tr.find('td', class_='bdlDate')
        number_tag = tr.find('td', class_='bdlNum noti')
        if title_tag and user_tag and date_tag:
            title = title_tag.get_text(strip=True)
            link = title_tag.find('a')['href'] if title_tag.find('a') else None
            user = user_tag.get_text(strip=True)
            date = date_tag.get_text(strip=True)
            number = number_tag.get_text(strip=True) if number_tag else None
            notice = {
                'number': number,
                'sort': cd_num,
                'title': title,
                'link': "https://www.pknu.ac.kr/main/163" + link if link else None,
                'user': user,
                'date': date,
            }
            notices.append(notice)
    return notices


def main():
    insert_to_firebase = True
    url_origin = 'https://www.pknu.ac.kr/main/163?pageIndex='
    cd_list = ["10001", "10002", '10003', '10004', '10007']
    start_page = 1  # 시작 페이지 번호
    end_page = 30  # 마지막 페이지 번호

    initial_setting()
    notices = []
    crawling_start_time = time.time()
    
    
    # 병렬 처리를 위한 ThreadPoolExecutor 생성
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for page_num in range(start_page, end_page + 1):
            for cd_num in cd_list:
                url = f"{url_origin}{page_num}&bbsId=2&searchCondition=title&searchKeyword=&cd={cd_num}"
                # 병렬 실행을 위한 작업 등록
                futures.append(executor.submit(main_crawling, url, cd_num))
        
        for future in as_completed(futures):
            # 결과 집계
            crawl_result = future.result()
            notices.extend(crawl_result)
    #크롤링 종료 시간 기록 및 소요 시간 계산
    crawling_end_time = time.time()
    crawling_duration = crawling_end_time - crawling_start_time
    # 데이터베이스에 공지사항 삽입 (병렬 처리 없음)
    if insert_to_firebase:
        insert_start_time = time.time()
        process_notices(notices, insert_to_firebase)
        insert_time = time.time() - insert_start_time
        print(f"Insertion time: {insert_time:.2f} seconds")
    else:
        process_notices(notices, insert_to_firebase)
    print(f"Crawling time: {crawling_duration:.2f} seconds")
    print(f"Total number of notices: {len(notices)}")
    print("Crawling complete.")

if __name__ == "__main__":
    main()