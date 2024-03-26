import requests
from bs4 import BeautifulSoup
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import hashlib
import json
from dotenv import load_dotenv
import os
# Firebase 초기 설정


def initial_setting():
    # .env 파일에서 환경변수를 불러옵니다.
    load_dotenv()
    cred = credentials.Certificate('./firebase_admin_key.json')
    firebase_database_url = os.getenv('FIREBASE_DATABASE_URL')
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
    # 삭제할 공지사항의 데이터 조회
    notice_to_remove = notices_ref.child(hash_to_remove).get()
    notices_ref.child(hash_to_remove).delete()
    metadata_ref.child(hash_to_remove).delete()

    print(f"Removed notice: {notice_to_remove['number']} - {notice_to_remove['title']}")

# 공지사항 데이터 처리


def process_notices(notices):
    existing_hashes = get_existing_hashes()
    #print("Initial existing_hashes: ", existing_hashes)
    
    # 처리 결과를 알기 쉽게 출력하기 위한 변수
    initial_count = len(existing_hashes)  # 초기 공지사항 수
    print(f"Initial number of notices: {initial_count}")

    update_count = 0  # 업데이트된 공지사항 수
    remove_count = 0  # 삭제된 공지사항 수

    # 공지사항 데이터로부터 해시 코드 리스트 생성
    new_hashes = {generate_hash(notice) for notice in notices}
    #print("New hashes from notices: ", new_hashes)

    # 수정 및 추가를 위한 해시 코드
    to_update = new_hashes - existing_hashes
    #print("To update: ", to_update)

    # 삭제를 위한 해시 코드
    to_remove = existing_hashes - new_hashes
    #print("To remove: ", to_remove)

    # 수정 및 추가 실행
    for notice in notices:
        notice_hash = generate_hash(notice)
        if notice_hash in to_update:
            update_notice(notice, notice_hash)
            update_count += 1

    # 삭제 실행
    for hash_to_remove in to_remove:
        remove_notice(hash_to_remove)
        remove_count += 1
        
    final_count = initial_count - remove_count + update_count  # 최종 공지사항 수
    print(f"Updated notices: {update_count}")
    print(f"Removed notices: {remove_count}")
    print(f"Final number of notices: {final_count}")
    print("Database update complete.")


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
            number = number_tag.get_text(
                strip=True) if number_tag else None  # Adjusted to handle None
            notice = {
                'number': number,
                'sort': cd_num,
                'title': title,
                # Adjusted to handle None
                'link': "https://www.pknu.ac.kr/main/163" + link if link else None,
                'user': user,
                'date': date,
            }
            notices.append(notice)
    return notices


if __name__ == "__main__":
    isTest = False
    url_origin = 'https://www.pknu.ac.kr/main/163?pageIndex=1&bbsId=2&searchCondition=title&searchKeyword=&cd='
    cd_list = ["10001", "10002", '10003', '10004', '10007']
    initial_setting()
    notices = []
    for cd_num in cd_list:        
        url = url_origin + cd_num
        notices.extend(main_crawling(url, cd_num))
    process_notices(fake_crawled_data if isTest else notices)
    print("Crawling complete.")
