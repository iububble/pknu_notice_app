import requests
from bs4 import BeautifulSoup as bs
from tqdm.notebook import tqdm
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import json
import os

def extract_major_url():

    major_info = {}

    url = f"https://www.pknu.ac.kr/main/23"
    html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"\
    "(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "\
    "Chrome/110.0.0.0 Safari/537.36"}, verify=False)
    html.encoding = 'utf-8'
    soup = bs(html.text, "lxml")

    tables = soup.find_all('table')

    for table in tables:
        tbody = table.find('tbody')
        trs = tbody.find_all('tr')
        for tr in trs:
            majors = tr.find_all('td', class_ = 'search')
            if majors[1].text.strip() == '-':
                major_name = majors[0].text.strip()
            else:
                major_name = majors[1].text.strip()
            atags = tr.find('a')
            if atags:
                major_link = atags.get('href')
            major_info[major_name] = major_link
    
    return major_info


def save_notice_data(file_path, major_name, row_info):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            json.dump({}, file)
    
    with open(file_path, 'r') as file:
        existing_data = json.load(file)
    
    if major_name not in existing_data:
        existing_data[major_name] = {}
    
    new_key = f"key_{len(existing_data[major_name]) + 1}"
    existing_data[major_name][new_key] = row_info
    
    with open(file_path, 'w') as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=4)


"--------------------------crawling code for old version page--------------------------"

def extract_old_row_info(row):

    title = row.find_element(By.TAG_NAME, "h4")
    update_date = row.find_element(By.CLASS_NAME, "date")
    hyperlink = row.find_element(By.TAG_NAME, "a")
    link_to_notice = hyperlink.get_attribute("href")
    writer = row.find_element(By.CLASS_NAME, "writer")
    
    return {
        "date": update_date.text,
        "link": link_to_notice,
        "title": title.text,
        "user": writer.text
    }


def get_old_notice_rows(driver, major_url):

    driver.get(major_url)

    page_info = driver.find_element(By.CLASS_NAME, "page").text
    last_page = int(page_info.split("/")[-1])
    current_page = 1

    print(last_page)
    while current_page <= last_page:
        major_name = driver.title

        if current_page > 1:
            # 페이지 번호가 포함된 URL로 이동
            current_url = major_url + f"&pageIndex={current_page}"
            driver.get(current_url)

        board_table = driver.find_element(By.ID, "board_list")
        rows = board_table.find_elements(By.TAG_NAME, "li")

        for row in rows:
            row_info = extract_old_row_info(row)
            save_notice_data('./test_3.json', major_name, row_info)
            print(extract_old_row_info(row))

        current_page += 1






    # for row in rows:
    #     print(extract_old_row_info(row))

"--------------------------crawling code for new version page--------------------------"

def extract_row_info(row):

    text = row.find_element(By.CLASS_NAME, "bdlTitle")
    update_date = row.find_element(By.CLASS_NAME, "bdlDate")
    writer = row.find_element(By.CLASS_NAME, "bdlUser")
    hyperlink = row.find_element(By.TAG_NAME, "a")
    link_to_notice = hyperlink.get_attribute("href")
    
    return {
        "date": update_date.text,
        "link": link_to_notice,
        "title": text.text,
        "user": writer.text
    }


def get_notice_rows(driver, major_url):

    driver.get(major_url)

    # brd_list 태그가 a, b, c 인 경우에 따라 분류
    b_brd_list = ["ref"]
    c_brd_list = ["fashion", "control", "semiconductor", "humanict", "humanbio"]

    brd_alphabet = "a"
    brd_alphabet = "b" if any(word in major_url for word in b_brd_list) else brd_alphabet
    brd_alphabet = "c" if any(word in major_url for word in c_brd_list) else brd_alphabet

    board_top = driver.find_element(By.CLASS_NAME, f"{brd_alphabet}_brdTop")
    table_body = board_top.find_elements(By.TAG_NAME, "p")
    page_info = table_body[0].text

    last_page = int(page_info.split("/")[-1])
    current_page = 1

    while current_page <= last_page:
        major_name = driver.title.split("|")[-1]

        if current_page > 1:
            # 페이지 번호가 포함된 URL로 이동
            current_url = major_url + f"?pageIndex={current_page}"
            driver.get(current_url)

        board_table = driver.find_element(By.CLASS_NAME, f"{brd_alphabet}_brdList")
        table_body = board_table.find_elements(By.TAG_NAME, "tbody")
        rows = table_body[0].find_elements(By.TAG_NAME, "tr")

        for row in rows:
            row_info = extract_row_info(row)
            save_notice_data('./test_2.json', major_name, row_info)
            print(extract_row_info(row))

        current_page += 1


def main():
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    major_urls = [
    # "https://kukmun.pknu.ac.kr/korean/5186",
    # "https://english.pknu.ac.kr/english/3936",
    # "https://econ.pknu.ac.kr/econ/2836",
    # "https://pknulaw.pknu.ac.kr/pknulaw/3917",
    # "https://pknupa.pknu.ac.kr/pknupasw/3153",
    # "https://dias.pknu.ac.kr/dias/3996",
    # "https://chinese.pknu.ac.kr/chinese/4288",
    # "https://education.pknu.ac.kr/education/1553",
    # "https://math.pknu.ac.kr/math/339",
    # "https://physics.pknu.ac.kr/physics/543",
    # "https://chem.pknu.ac.kr/chem/2180",
    # "https://microbiology.pknu.ac.kr/microbiology/390",
    # "https://nursing.pknu.ac.kr/nursing/432",
    # "https://scicomp.pknu.ac.kr/scicomp/575",
    # "https://dba.pknu.ac.kr/dba/1235",
    # "https://pknudic.pknu.ac.kr/pknudic/1193",
    # "https://electric-eng.pknu.ac.kr/electric-eng/4079",
    # "https://semicon.pknu.ac.kr/semicon/3684",
    # "https://me.pknu.ac.kr/me/1277",
    # "https://mae.pknu.ac.kr/mae/2217",
    # "https://mse.pknu.ac.kr/mse/5618",
    # "https://name.pknu.ac.kr/name/2486",
    # "https://induseng.pknu.ac.kr/induseng/1074",
    # "https://polymer.pknu.ac.kr/polymer/1315",
    # "https://nano.pknu.ac.kr/nano/1883",
    # "https://sme.pknu.ac.kr/sme/721",
    # "https://safety.pknu.ac.kr/safety/2078",
    # "https://fire.pknu.ac.kr/fire/867",
    # "https://metal.pknu.ac.kr/metal/2250",
    # "https://materials-engineering.pknu.ac.kr/materials-eng/5775",
    # "https://materials.pknu.ac.kr/materials/910",
    # "https://archieng.pknu.ac.kr/archieng/1423",
    # "https://civil.pknu.ac.kr/civil/5345",
    # "https://ecoeng.pknu.ac.kr/ecoeng/5664",
    # "https://nulife.pknu.ac.kr/nulife/4403",
    # "https://biotech.pknu.ac.kr/biotech/4159",
    # "https://aqua-culture.pknu.ac.kr/aqua-culture/4174",
    # "https://marinebio.pknu.ac.kr/marinebio/4123",
    # "https://aquamed.pknu.ac.kr/aquamed/4229",
    # "https://fedu.pknu.ac.kr/fedu/4470",
    # "https://mbe.pknu.ac.kr/mbe/5478",
    # "https://ree.pknu.ac.kr/ree/2824",
    # "https://env-eng.pknu.ac.kr/env-eng/1996",
    # "https://pkuocean.pknu.ac.kr/pkuocean/1485",
    # "https://earth.pknu.ac.kr/earth/1646",
    # "https://envatm.pknu.ac.kr/envatm/2268",
    # "https://oceaneng.pknu.ac.kr/oceaneng/942",
    # 'https://ere.pknu.ac.kr/ere/1455',
    # "https://icms.pknu.ac.kr/bigdata/599",
    # "https://stat.pknu.ac.kr/stat/404",
    # "https://icms.pknu.ac.kr/comm/4926",  
    # "https://marinesports.pknu.ac.kr/marinesports/2041",
    # "https://ee.pknu.ac.kr/ee/1669",
    # "https://ice.pknu.ac.kr/pknuice/895",
    # "https://pknuarchi.pknu.ac.kr/pknuarchi/969",
    # "https://industrial.pknu.ac.kr/industrial/3715",
    # "https://ce.pknu.ac.kr/ce/1814",
    # "https://icms.pknu.ac.kr/smartmobility/5454",
    # "https://lifelong.pknu.ac.kr/lifelong/4038",
    # "https://safe.pknu.ac.kr/safe/1342",
    # "https://msce.pknu.ac.kr/msce/4627",
    # "https://eese.pknu.ac.kr/eese/4055",
    # "https://duem.pknu.ac.kr/duem/1592",
    # "https://fashion.pknu.ac.kr/fashion/2128",
    # "https://control.pknu.ac.kr/control/3883",
    # "https://semiconductor.pknu.ac.kr/semiconductor/5517",
    # "https://icms.pknu.ac.kr/humanict/652",
    # "https://humanbio.pknu.ac.kr/humanbio/2886",
    # "https://ref.pknu.ac.kr/ref/1783",
    "https://cms.pknu.ac.kr/japanese/view.do?no=12239",
    "https://cms.pknu.ac.kr/history/view.do?no=17587",
    "https://cms.pknu.ac.kr/politics/view.do?no=16877",
    "https://cms.pknu.ac.kr/chemeng/view.do?no=10696",
]

    for major_url in major_urls:
        print(major_url)

        if "//cms.pknu.ac.kr" in major_url:
            get_old_notice_rows(driver, major_url)
        else:
            get_notice_rows(driver, major_url)
    driver.quit()

if __name__ == "__main__":
    main()