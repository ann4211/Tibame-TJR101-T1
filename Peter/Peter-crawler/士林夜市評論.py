from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time, csv, os, random

# 建立資料夾
os.makedirs("Peter/Data", exist_ok=True)

# 啟動瀏覽器
options = Options()
options.add_argument("user-agent=your-random-user-agent")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 開啟地圖
driver.get("https://www.google.com/maps/search/%E5%A3%AB%E6%9E%97%E5%A4%9C%E5%B8%82/@25.088873,121.5223389,17z/data=!3m1!4b1?entry=ttu&g_ep=EgoyMDI1MDQyMi4wIKXMDSoASAFQAw%3D%3D")
time.sleep(2)

print('-----------------------------------------------------------------------------------------------------------------------')

# 等待並點擊「士林夜市」的搜尋結果
try:
    shilin_market = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@aria-label='士林夜市']"))
    )
    shilin_market.click()
    print("成功點擊士林夜市")
    time.sleep(2)  # 等待頁面加載
except TimeoutException as e:
    print("等待士林夜市按鈕超時:", e)
except Exception as e:
    print("點擊士林夜市時發生其他錯誤:", e)

print('-----------------------------------------------------------------------------------------------------------------------')

# 往下滑動直到看到「更多評論」按鈕並點擊它
try:
    scrollable_div = driver.find_element(By.XPATH, '//div[contains(@class, "m6QErb DxyBCb kA9KIf dS8AEf XiKgde")]')
    
    for _ in range(10):  # 最多嘗試 10 次
        # 模擬人類行為，隨機延遲
        time.sleep(2)

        # 檢查是否已經找到「更多評論」按鈕
        try:
            more_reviews_button = driver.find_element(By.XPATH, "//span[contains(@class, 'wNNZR fontTitleSmall') and contains(text(), '更多評論')]")
            if more_reviews_button.click():
                print("成功點擊「更多評論」按鈕")
                time.sleep(2)  # 等待頁面加載
                break
        except Exception:
            print("未找到『更多評論』按鈕，繼續滾動...")
            continue
except Exception as e:
    print("滑動頁面時發生錯誤:", e)

print('-----------------------------------------------------------------------------------------------------------------------')

# 找到「更多評論」按鈕並滾動到底部
try:
    # 找到評論區塊
    scrollable_div = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "m6QErb DxyBCb kA9KIf dS8AEf XiKgde")]'))
    )
    previous_height = 0
    total_scroll_attempts = 0  # 計算滾動次數
    max_scroll_attempts = 500  # 設定最大滾動次數，適合處理大量評論
    previous_comment_count = 0  # 上一次評論數量

    while total_scroll_attempts < max_scroll_attempts:
        # 滾動到頁面底部
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
        time.sleep(random.uniform(3, 5))  # 模擬人類行為，隨機延遲 3 到 5 秒

        # 獲取當前高度
        current_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)

        # 檢查評論數量是否增加
        comments = driver.find_elements(By.XPATH, '//div[@aria-label="評論"]')
        current_comment_count = len(comments)
        print(f"當前評論數量：{current_comment_count}")
        if current_comment_count > previous_comment_count:
            print(f"評論數量增加：{current_comment_count} 筆")
            previous_comment_count = current_comment_count
        else:
            print("評論數量未增加，可能已到達頁面底部")

        # 如果高度沒有變化，嘗試多次確認是否真的到達底部
        if current_height == previous_height:
            print("檢查是否已到達頁面底部...")
            time.sleep(2)  # 再次等待 2 秒確認是否有新內容加載
            current_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
            if current_height == previous_height:
                print("已到達頁面底部，停止滾動")
                break

        # 更新高度並增加滾動次數
        previous_height = current_height
        total_scroll_attempts += 1
        print(f"已滾動 {total_scroll_attempts} 次...")

    print("完成滾動，所有評論已加載")
except Exception as e:
    print("滾動評論區時發生錯誤:", e)

# 停止幾秒鐘，讓使用者可以觀察結果
print("等待 15 秒以觀察結果...")
time.sleep(15)

print('-----------------------------------------------------------------------------------------------------------------------')

comments = driver.find_elements(By.XPATH, '//div[@aria-label="評論"]')
current_comment_count = len(comments)
print(f"當前評論數量：{current_comment_count}")



# 抓評論區塊
comments = driver.find_elements(By.XPATH, '//div[@aria-label="評論"]')
data = []
seen_comments = set()

for c in comments:
    try:
        # 檢查是否有「全文」按鈕，如果有就點開
        try:
            full_text_button = c.find_element(By.XPATH, ".//button[@aria-label='顯示更多']")
            if full_text_button.is_displayed():
                ActionChains(driver).move_to_element(full_text_button).click().perform()
                time.sleep(0.5)  # 等一下再抓全文
        except:
            pass  # 沒有顯示更多按鈕也沒關係

        # 抓評論者名稱
        author = c.find_element(By.XPATH, ".//div[contains(@class, 'd4r55')]").text

        # 抓評論星等（透過 aria-label 裡的文字，例如「5顆星」）
        rating_element = c.find_element(By.XPATH, ".//span[contains(@aria-label, '顆星')]")
        rating = rating_element.get_attribute("aria-label")

        # 抓評論內容
        content = c.find_element(By.XPATH, ".//span[contains(@class, 'wiI7pd')]").text

        # 抓評論時間
        time_tag = c.find_element(By.XPATH, ".//span[contains(@class, 'rsqaWe')]").text

        # 去重複：作者 + 內容 作為唯一標記
        comment_key = (author, content)
        if comment_key not in seen_comments:
            seen_comments.add(comment_key)
            # 儲存評論資訊
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

print(f"✅ 成功抓取 {len(data)} 筆評論，儲存到 Peter/Data/士林夜市評論.csv！")
