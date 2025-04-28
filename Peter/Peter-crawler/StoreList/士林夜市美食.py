from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, csv, os


# 設定 Chrome 啟動選項
chrome_options = Options()
chrome_options.add_argument("--headless")  # 無頭模式
chrome_options.add_argument("--no-sandbox")  # 重要！Docker 裡要加
chrome_options.add_argument("--disable-dev-shm-usage")  # 避免資源問題
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-infobars")

# 啟動 Chrome
driver = webdriver.Chrome(options=chrome_options)

# 開啟 Google Maps 並搜尋
driver.get("https://www.google.com.tw/maps/search/%E5%A3%AB%E6%9E%97%E5%A4%9C%E5%B8%82%E7%BE%8E%E9%A3%9F/@25.0888827,121.5223389,682m/data=!3m2!1e3!4b1?entry=ttu&g_ep=EgoyMDI1MDQyMy4wIKXMDSoASAFQAw%3D%3D")
time.sleep(2)

try:
    # 找到滾動的主要區塊
    scrollable_div = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]'))
    )
    previous_height = 0
    total_scroll_attempts = 0
    max_scroll_attempts = 500

    while total_scroll_attempts < max_scroll_attempts:
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
        time.sleep(2)
        current_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)

        if current_height == previous_height:
            print("檢查是否已到達頁面底部...")
            time.sleep(2)
            current_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
            if current_height == previous_height:
                print("✅ 已到達頁面底部，停止滾動")
                break

        previous_height = current_height
        total_scroll_attempts += 1

    print("完成滾動，所有內容已加載")
except Exception as e:
    print("滾動區塊時發生錯誤:", e)

# === 抓取所有卡片 ===
results = []
cards = driver.find_elements(By.XPATH, '//a[contains(@class, "hfpxzc")]')

for card in cards:
    try:
        name = card.get_attribute("aria-label")
        url = card.get_attribute("href")
        if name and url:
            results.append({"name": name, "url": url})
    except Exception as e:
        print(f"擷取店家資訊失敗: {e}")
        continue


# === 儲存成 CSV ===
output_path = os.path.join("Peter/Data/StoreList/士林夜市美食.csv")
with open(output_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "url"])
    writer.writeheader()
    writer.writerows(results)

print(f"✅ 共抓到 {len(results)} 筆資料，已存到 {output_path}")

driver.quit()
