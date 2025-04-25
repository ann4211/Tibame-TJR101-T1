import csv
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import random

# ✅ 啟動瀏覽器
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

with open("一中商圈攤位評論.csv", "w", encoding="utf-8-sig", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["店家名稱", "評分", "留言者名稱", "留言者身分", "留言時間", "評論內容"])
    print("標題寫入完成")

    # 讀取店家清單
    df = pd.read_csv("一中店家清單.csv")
    for name, link in zip(df['names'], df['links']):
        try:
            driver.get(link)
            wait = WebDriverWait(driver,10,0.1)
            print(f"進入攤位{name}")
        except:
            print("門沒開，進不去")

    # ▶️ 點擊「更多評論」
        try:
            review_button = driver.find_element(By.XPATH, "//div[text()='評論']")
            # 這段可以突破被遮住或非互動元素的情況
            driver.execute_script("arguments[0].click();", review_button)
            print("✅ 成功點擊『評論』按鈕")
            time.sleep(3)
        except Exception as e:
            print("⚠️ 找不到評論按鈕，可能無評論")
            continue
    
            # 點擊「排序」按鈕
        try:
            sort_button = WebDriverWait(driver, 10, 0.1).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="排序評論"]'))
            )
            sort_button.click()
            print("排序按鈕已點擊")
        except Exception as e:
            print("點擊排序按鈕失敗:", e)

        # 嘗試抓出所有選項文字，確認有「最新」
        WebDriverWait(driver, 5, 0.1).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="action-menu"]/div[2]'))
        )
        menu_items = driver.find_elements(By.XPATH, '//*[@id="action-menu"]//div[@role="menuitem"]')
        for item in menu_items:
            if "最新" in item.text:
                driver.execute_script("arguments[0].scrollIntoView(true);", item)
                driver.execute_script("arguments[0].click();", item)
                print("成功點擊『最新』")
                break
            else:
                print("❌ 沒有找到『最新』選項")
    

        # 嘗試 JavaScript 強制點「最新」
        try:
            latest_option = WebDriverWait(driver, 10, 0.1).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="action-menu"]/div[2]'))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", latest_option)
            driver.execute_script("arguments[0].click();", latest_option)
            print("成功點擊最新")
        except Exception as e:
            print("點擊最新失敗:", e)

    # 🔽 滾動評論區
        try:
            scrollable_div = WebDriverWait(driver, 10, 0.1).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='m6QErb DxyBCb kA9KIf dS8AEf XiKgde ']"))
            )
            print("找到評論滾動容器")
        except Exception as e:
            print("⚠️ 找不到評論滾動容器:", e)
            

    # ✅ 滾動直到沒有新評論出現
        scroll_count = 0
        unchanged_count = 0
        max_unchanged = 5  # 最多允許幾次沒有新增評論就結束

        while True:
            pre = len(driver.find_elements(By.CLASS_NAME, "jftiEf"))
            print("向下滾動中...")
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
            time.sleep(random.uniform(1, 2))
            post = len(driver.find_elements(By.CLASS_NAME, "jftiEf"))
            scroll_count += 1
            
            if post == pre:
                unchanged_count += 1
                print(f"評論數未增加{unchanged_count}次")
                if unchanged_count >= max_unchanged:
                    print(f"已顯示所有評論，共有{post}篇評論")
                    break
            else:
                unchanged_count = 0
                print(f"⬇️ 第 {scroll_count} 次滾動，目前共 {post} 則評論")

            if scroll_count % 5 == 0:
                print("⏸️ 模擬使用者停下來閱讀評論...")
                time.sleep(random.uniform(1, 2))

        # 📥 擷取評論
        reviews = driver.find_elements(By.CLASS_NAME, "jftiEf")
        print(f"💬 共找到 {len(reviews)} 則評論")

        count = 0
        for review in reviews:
            try:
                author = review.find_element(By.CLASS_NAME, "d4r55").text
            except:
                author = ''
                print("抓取使用者名稱錯誤")

            try:
                identity = review.find_element(By.CLASS_NAME, "RfnDt").text
            except:
                identity = ''
                print("抓取使用者身分錯誤")
            
            try:
                rating = review.find_element(By.CLASS_NAME, "kvMYJc").get_attribute("aria-label")
            except:
                rating = ''
                print("抓取評分錯誤")
            try:
                time_text = review.find_element(By.CLASS_NAME, "rsqaWe").text
            except:
                time_text = ''
                print("抓取時間錯誤")    
            try:    
                comment_el = review.find_element(By.CLASS_NAME, "wiI7pd")
                try:
                    # ▶️ 點擊「顯示完整內容」的按鈕
                    button = comment_el.find_element(By.CSS_SELECTOR, "button.w8nwRe.kyuRq")
                    driver.execute_script("arguments[0].click()", button)
                    time.sleep(0.5)
                    print("點擊全文按鈕")
                except:
                    pass
                comment = comment_el.text
            except:
                comment = ''
                print(f"第{count+1}筆評論無內文")
            
            writer.writerow([name, rating, author, identity, time_text, comment])
            count += 1
            print(f"寫入第{count}筆評論")

        print(f"攤位{name}的評論已收集")

driver.quit()
print("\n✅ 所有評論已成功寫入 一中商圈攤位評論.csv！")
