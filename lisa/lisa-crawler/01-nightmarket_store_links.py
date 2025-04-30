import pandas as pd
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from random import uniform

def check_load_new_data(driver,class_):
    req = driver.page_source
    soup = BeautifulSoup(req,'html.parser')
    return len(soup.find_all("div",class_=class_))

def nightmarket_store_links(night_market, chinese_name):
    driver = Chrome()

    df = pd.read_csv(f"./data/input/{night_market}.csv")
    driver.get(f"https://www.google.com/maps/search/{chinese_name}")

    names = list()
    links = list()

    for index, row in df.iterrows():
        store = row[night_market]
        try:
            # 等待頁面加載結果，EC.presence_of_element_located是等到某的頁面出現
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "searchboxinput"))
            )
            search_box.clear()
            search_box.send_keys(chinese_name + store)
            search_box.send_keys(Keys.RETURN)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='QA0Szd']"))
            )

            time.sleep(2)

            req = driver.page_source
            soup = BeautifulSoup(req, 'html.parser')

            # 嘗試找到多筆資料
            restaurants = soup.select("div.Nv2PK")
            
            if len(restaurants) > 1:
                # 有多筆資料，抓取多間餐廳
                for restaurant in restaurants:
                    info = restaurant.find('a')
                    if info:
                        names.append(info.get('aria-label', '無名稱'))
                        links.append(info.get('href', '無連結'))
                time.sleep(2)

            else:
                # 只有一筆資料，直接取得當前頁面的 URL
                time.sleep(2)
                name = driver.find_element(By.XPATH, '//h1[@class="DUwDvf lfPIob"]').text
                link = driver.current_url
                names.append(name)
                links.append(link)

        except Exception as e:
            print(f"Error while processing store {store}: {e}")

    # 資料存到CSV
    df = pd.DataFrame({"餐廳名稱": names, "餐廳連結": links})
    df.to_csv(f"./data/output/store_list/{night_market}.csv", index=False, header=True, encoding='utf-8-sig')
    df.info()

    time.sleep(2)
    driver.close()

if __name__ == "__main__":
    night_markets = {
        "Dadong Night Market": "大東夜市",
        "Tainan Flower Night Market": "台南花園夜市",
        "Wusheng Night Market": "武聖夜市"
    }
    for night_market, chinese_name in night_markets.items():
        nightmarket_store_links(night_market, chinese_name)
