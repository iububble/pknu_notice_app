from bs4 import BeautifulSoup as bs
from tqdm.notebook import tqdm
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# ################ 식품공학전공, 해양생산시스템관리학부

def extract_row_info(row):

    # title = row.find_element(By.CLASS_NAME, "bdlTitle")
    update_date = row.find_element(By.CLASS_NAME, "date")
    hyperlink = row.find_element(By.TAG_NAME, "a")
    title = hyperlink.text
    link_to_notice = hyperlink.get_attribute("href")
    writer = row.find_element(By.CLASS_NAME, "writer.m_none")

    return title, update_date.text, link_to_notice, writer.text


def get_notice_rows(driver, major_url):

    driver.get(major_url)
    board_table = driver.find_element(By.CLASS_NAME, "tbl_01")
    table_body = board_table.find_elements(By.TAG_NAME, "tbody")
    rows = table_body[0].find_elements(By.TAG_NAME, "tr")
    
    for row in rows:
        print(extract_row_info(row))

################ 의공학과

def extract_row_info(row):

    title = row.find_element(By.CLASS_NAME, "td_subject")
    update_date = row.find_element(By.CLASS_NAME, "td_datetime")
    hyperlink = row.find_element(By.TAG_NAME, "a")
    link_to_notice = hyperlink.get_attribute("href")
    writer = row.find_element(By.CLASS_NAME, "sv_member")

    return title.text, update_date.text, link_to_notice, writer.text


def get_notice_rows(driver, major_url):

    driver.get(major_url)
    board_table = driver.find_element(By.CLASS_NAME, "tbl_head01.tbl_wrap")
    table_body = board_table.find_elements(By.TAG_NAME, "tbody")
    rows = table_body[0].find_elements(By.TAG_NAME, "tr")
    
    for row in rows:
        print(extract_row_info(row))


################ 시각디자인전공

def extract_row_info(row):

    hyperlink = row.find_element(By.TAG_NAME, "a")
    link_to_notice = hyperlink.get_attribute("href")

    return row.text, link_to_notice,


def get_notice_rows(driver, major_url):

    driver.get(major_url)
    board_table = driver.find_element(By.CLASS_NAME, "c_glyList")
    # table_body = board_table.find_elements(By.TAG_NAME, "tbody")
    rows = board_table.find_elements(By.TAG_NAME, "li")
    
    for row in rows:
        print(extract_row_info(row))


############### 위성정보융합공학전공

def extract_row_info(row):

    # update_date = row.find_element(By.CLASS_NAME, "td_datetime")
    hyperlink = row.find_element(By.TAG_NAME, "a")
    title = hyperlink.text
    link_to_notice = hyperlink.get_attribute("href")
    tds = row.find_elements(By.TAG_NAME, "td")
    writer, update_date = tds[2], tds[3]

    return title, link_to_notice, writer.text, update_date.text


def get_notice_rows(driver, major_url):

    driver.get(major_url)
    board_table = driver.find_element(By.CLASS_NAME, "list_normal_D")
    table_body = board_table.find_elements(By.TAG_NAME, "tbody")
    rows = table_body[0].find_elements(By.TAG_NAME, "tr")
    
    for row in rows:
        print(extract_row_info(row))


def main():

    unavailable_urls = [
    # "https://food.pknu.ac.kr/view.do?no=401",  
    # "http://bme.pknu.ac.kr/bbs/board.php?bo_table=notice", 
    # "https://visual.pknu.ac.kr/visual/3688",
    # "https://mpsm.pknu.ac.kr/view.do?no=303",
    "http://geoinfo.pknu.ac.kr//05piazza/08.php",
]

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    for majors in unavailable_urls:
        print("major : ", majors)
        get_notice_rows(driver, majors)
    driver.quit()


if __name__ == "__main__":
    main()