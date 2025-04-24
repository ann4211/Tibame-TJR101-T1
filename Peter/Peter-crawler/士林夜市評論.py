from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import os

# 建立資料夾
os.makedirs("Peter/Data", exist_ok=True)

# 啟動瀏覽器
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# 開啟地圖
driver.get("https://www.google.com/maps/place/%E5%A3%AB%E6%9E%97%E5%A4%9C%E5%B8%82/@25.0884972,121.5221617,17z/data=!3m1!5s0x3442aeb00c7fecbb:0xc0060360854178c2!4m10!1m2!2m1!1z5aOr5p6X5aSc5biC!3m6!1s0x3442aeb1c4fdaf05:0xe7c26dbe86e7f929!8m2!3d25.0884972!4d121.5243504!15sCgzlo6vmnpflpJzluIJaECIO5aOrIOaelyDlpJzluIKSAQxuaWdodF9tYXJrZXTgAQA!16zL20vMDZsc2Iz?entry=ttu")
time.sleep(2)

# 等待「更多評論」按鈕可見並點擊
try:
    more_reviews_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, '顯示更多')]"))
    )
    more_reviews_button.click()
    time.sleep(5)  # 等待評論加載
except Exception as e:
    print("沒找到更多評論按鈕:", e)

# 點擊「全文」以顯示完整評論
try:
    full_text_buttons = driver.find_elements(By.XPATH, "//button[@aria-label='顯示更多']")
    for button in full_text_buttons:
        ActionChains(driver).move_to_element(button).click().perform()
    time.sleep(3)  # 等待評論完整顯示
except Exception as e:
    print("點擊 '全文' 錯誤:", e)

# 捲動評論面板
try:
    scrollable_div = driver.find_element(By.XPATH, '//div[@aria-label="評論"]')
    for _ in range(10):  # 增加捲動次數，抓取更多評論
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
        time.sleep(2)
except Exception as e:
    print("捲動錯誤:", e)

# 抓評論區塊
comments = driver.find_elements(By.XPATH, '//div[@data-review-id]')
data = []
seen_comments = set()

for c in comments:
    try:
        author = c.find_element(By.XPATH, ".//button//div[contains(@class, 'd4r55')]").text
        rating = c.find_element(By.XPATH, ".//span[contains(@aria-label, '顆星')]").get_attribute("aria-label")
        content = c.find_element(By.XPATH, ".//span[contains(@class, 'wiI7pd')]").text
        time_tag = c.find_element(By.XPATH, ".//span[contains(@class, 'rsqaWe')]").text

        comment_key = (author, content)
        if comment_key not in seen_comments:
            seen_comments.add(comment_key)
            data.append({
                "author": author,
                "rating": rating,
                "content": content,
                "time": time_tag
            })
    except Exception as e:
        print("單一評論抓取錯誤:", e)

# 儲存成 CSV
with open("Peter/Data/士林夜市評論.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["author", "rating", "content", "time"])
    writer.writeheader()
    writer.writerows(data)

print(f"✅ 成功抓取 {len(data)} 筆評論，儲存到 data/士林夜市評論.csv！")
driver.quit()