# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time, csv, os


# # 設定 Chrome 啟動選項
# chrome_options = Options()
# chrome_options.add_argument("--headless")  # 無頭模式
# chrome_options.add_argument("--no-sandbox")  # 重要！Docker 裡要加
# chrome_options.add_argument("--disable-dev-shm-usage")  # 避免資源問題
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--window-size=1920,1080")
# chrome_options.add_argument("--disable-extensions")
# chrome_options.add_argument("--start-maximized")
# chrome_options.add_argument("--disable-infobars")

# # 啟動 Chrome
# driver = webdriver.Chrome(options=chrome_options)


# # 開啟地圖
# driver.get("https://www.google.com.tw/maps/place/%E5%A3%AB%E6%9E%97%E5%A4%9C%E5%B8%82/@25.088502,121.5217755,682m/data=!3m3!1e3!4b1!5s0x3442aeb00c7fecbb:0xc0060360854178c2!4m6!3m5!1s0x3442aeb1c4fdaf05:0xe7c26dbe86e7f929!8m2!3d25.0884972!4d121.5243504!16zL20vMDZsc2Iz?entry=ttu&g_ep=EgoyMDI1MDQyMy4wIKXMDSoASAFQAw%3D%3D")
# time.sleep(2)




# # 找到「更多評論」按鈕並點擊
# try:
#     more_reviews_button = WebDriverWait(driver, 10).until(
#         EC.element_to_be_clickable((By.XPATH, '//button[contains(@aria-label, "更多評論")]'))
#     )
#     more_reviews_button.click()
#     print("成功點擊「更多評論」按鈕")
#     time.sleep(2)  # 等待評論區加載
# except Exception as e:
#     print("點擊「更多評論」按鈕失敗:", e)


# try:
#     # 找到滾動的主要區塊（改用 role="feed"）
#     scrollable_div = WebDriverWait(driver, 30).until(
#         EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]'))
#     )
#     previous_height = 0
#     total_scroll_attempts = 0
#     max_scroll_attempts = 500

#     while total_scroll_attempts < max_scroll_attempts:
#         driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
#         time.sleep(2)
#         current_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)

#         if current_height == previous_height:
#             print("檢查是否已到達頁面底部...")
#             time.sleep(2)
#             current_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
#             if current_height == previous_height:
#                 print("✅ 已到達頁面底部，停止滾動")
#                 break

#         previous_height = current_height
#         total_scroll_attempts += 1

#     print("完成滾動，所有內容已加載")
# except Exception as e:
#     print("滾動區塊時發生錯誤:", e)





# try:
#     # 找到評論區塊
#     scrollable_div = WebDriverWait(driver, 20).until(
#         EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]'))
#     )
#     previous_height = 0
#     total_scroll_attempts = 0  # 計算滾動次數
#     max_scroll_attempts = 500  # 設定最大滾動次數，適合處理大量評論
#     previous_comment_count = 0  # 上一次評論數量

#     while total_scroll_attempts < max_scroll_attempts:
#         # 滾動到頁面底部
#         driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
#         time.sleep(2)

#         # 獲取當前高度
#         current_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)

#         # 檢查評論數量是否增加
#         comments = driver.find_elements(By.XPATH, '//div[@aria-label="評論"]')
#         current_comment_count = len(comments)
#         print(f"當前評論數量：{current_comment_count}")
#         if current_comment_count > previous_comment_count:
#             print(f"評論數量增加：{current_comment_count} 筆")
#             previous_comment_count = current_comment_count
#         else:
#             print("評論數量未增加，可能已到達頁面底部")

#         # 如果高度沒有變化，嘗試多次確認是否真的到達底部
#         if current_height == previous_height:
#             print("檢查是否已到達頁面底部...")
#             time.sleep(2)  # 再次等待 2 秒確認是否有新內容加載
#             current_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
#             if current_height == previous_height:
#                 print("已到達頁面底部，停止滾動")
#                 break

#         # 更新高度並增加滾動次數
#         previous_height = current_height
#         total_scroll_attempts += 1

#     print("完成滾動，所有評論已加載")
# except Exception as e:
#     print("滾動評論區時發生錯誤:", e)





# # 抓評論區塊
# comments = driver.find_elements(By.XPATH, '//div[@data-review-id]')
# data = []
# seen_comments = set()  # 用來儲存已抓取過的評論（避免重複）












# for c in comments:
#     try:
#         # 檢查是否有「顯示更多」按鈕，如果有就點開
#         try:
#             full_text_button = c.find_element(By.XPATH, ".//button[@aria-label='顯示更多']")
#             if full_text_button.is_displayed():
#                 ActionChains(driver).move_to_element(full_text_button).click().perform()
#                 time.sleep(0.5)  # 等一下再抓全文
#         except Exception:
#             pass

#         # 抓評論者名稱
#         try:
#             author = c.find_element(By.XPATH, ".//div[contains(@class, 'ODSEW-ShBeI-title')]").text
#         except Exception:
#             author = "匿名"

#         # 抓評論星等（透過 aria-label 裡的文字，例如「5顆星」）
#         rating_element = c.find_element(By.XPATH, ".//span[contains(@aria-label, '顆星')]")
#         rating = rating_element.get_attribute("aria-label")

#         # 抓評論內容
#         content = c.find_element(By.XPATH, ".//span[contains(@class, 'wiI7pd')]").text

#         # 抓評論時間
#         time_tag = c.find_element(By.XPATH, ".//span[contains(@class, 'rsqaWe')]").text

#         # 去重複：作者 + 內容 作為唯一標記
#         comment_key = (author, content)
#         if comment_key not in seen_comments:
#             seen_comments.add(comment_key)
#             # 儲存評論資訊
#             data.append({
#                 "author": author,
#                 "rating": rating,
#                 "content": content,
#                 "time": time_tag
#             })

#     except Exception as e:
#         print("單一評論抓取錯誤:", e)


# # 儲存成 CSV
# with open("Peter/Data/Comment/士林夜市評論.csv", "w", encoding="utf-8", newline="") as f:
#     writer = csv.DictWriter(f, fieldnames=["author", "rating", "content", "time"])
#     writer.writeheader()
#     writer.writerows(data)

# print(f"✅ 成功抓取 {len(data)} 筆評論，儲存到 Peter/Data/士林夜市評論.csv！")
