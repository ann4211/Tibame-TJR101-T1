from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from utils import scroll_to_bottom
import time, csv, os

# 建立資料夾
os.makedirs("Peter/Data", exist_ok=True)

# 啟動瀏覽器
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# 開啟 Google Maps 並搜尋
driver.get("https://www.google.com/maps/search/士林夜市攤販/")
time.sleep(2)

# 自動滑到底
scroll_to_bottom(driver)

# 擷取所有店家名稱與連結
cards = driver.find_elements(By.CLASS_NAME, "hfpxzc")
results = []

for card in cards:
    try:
        name = card.get_attribute("aria-label")
        url = card.get_attribute("href")
        if name and url:
            results.append({"name": name, "url": url})
    except:
        continue

# 儲存成 CSV
with open("Peter/Data/士林夜市攤販.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "url"])
    writer.writeheader()
    writer.writerows(results)

print(f"✅ 共抓到 {len(results)} 筆店家資料，儲存到 data/士林夜市攤販.csv")
driver.quit()
