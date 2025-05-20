import csv
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import random

# # ✅ 啟動瀏覽器
options = webdriver.ChromeOptions()
options.binary_location = "/usr/bin/google-chrome"  # 加這行
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--headless")  # 如果你是跑在 server/container，通常要加這個
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# ✅ 啟動瀏覽器
# options = webdriver.ChromeOptions()
# options.add_argument("--start-maximized")
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

df = pd.read_csv("/workspaces/poetry-demo-test2/src/yizhong_store.csv")
stars = []
comments = []
levels = []
tag_alls = []
names = []
links = []
store_addresses = []
count = 0
total = len(df['names'])
for name, link, store_address in zip(df['names'], df['links'], df['address']):
    try:
        driver.get(link)
        wait = WebDriverWait(driver,10,0.1)
        print(f"進入攤位{name}")
    except:
        print("未進入店家成功!")
        pass

    try:
        star = driver.find_element(By.CLASS_NAME,"ceNzKf").get_attribute("aria-label").rstrip(" 顆星")
        print(f"爬取總評分數{star}成功")
    except:
        star = ''
        print("沒有總評分數")

    try:
        reviews = driver.find_element(By.CSS_SELECTOR, 'span[aria-label$="則評論"]')
        comment = reviews.get_attribute('aria-label')
        print(f"成功爬取總評論數{comment}")
    except:
        comment = ''
        print("沒有總評論數")
    
    try:
        level = driver.find_element(By.XPATH, '//span[@class="mgr77e"]/span/span[2]/span/span').text
        print(f"成功爬取店家消費等級{level}")
    except:
        level = ''
        print("沒有店家消費等級")

    try:
        review_button = driver.find_element(By.XPATH, "//div[text()='評論']")
        # 這段可以突破被遮住或非互動元素的情況
        driver.execute_script("arguments[0].click();", review_button)
        print("✅ 成功點擊『評論』按鈕")
        time.sleep(3)
    except :
        print("⚠️ 找不到評論按鈕，可能無評論")
    
    try:
        tag_list = driver.find_elements(By.XPATH,"//button[contains(@aria-label, '則評論提到')]")
        tags = [tag.get_attribute('aria-label').split("提到")[1] for tag in tag_list]
        tag_all = ','.join(tags)
        print(f"取得店家標籤標籤`{tag_all}`成功")
    except:
        tag_all = ''
        print("無取得標籤")

    count += 1
    print(f"已爬取{name}，目前完成{count}家/{total}家")

    stars.append(star)
    comments.append(comment)
    levels.append(level)
    tag_alls.append(tag_all)
    names.append(name)
    links.append(link)
    store_addresses.append(store_address)

data = {
    "店家名稱" : names,
    "店家地址" : store_addresses,
    "店家網址" : links,
    "店家評分" : stars,
    "店家價格" : levels,
    "店家評論" : comments,
    "店家標籤" : tag_alls
}

driver.quit()
time.sleep(1)

df = pd.DataFrame(data=data)
df.to_csv("yizhong_store_update.csv", index=None)
print("已完成所有店家更新")