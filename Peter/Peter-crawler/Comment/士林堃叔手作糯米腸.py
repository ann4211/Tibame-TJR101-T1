# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time, os, csv

# # 設定 Chrome 選項
# chrome_options = Options()
# chrome_options.add_argument("--headless")  # 啟用無頭模式
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--window-size=1920,1080")
# chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
# chrome_options.add_argument("--disable-gpu")

# driver = webdriver.Chrome(options=chrome_options)

# # 開啟 Google Maps 商家頁面
# driver.get("https://www.google.com.tw/maps/place/%E5%A3%AB%E6%9E%97%E5%A0%83%E5%8F%94%E6%89%8B%E4%BD%9C%E7%B3%AF%E7%B1%B3%E8%85%B8/data=!4m7!3m6!1s0x3442af677f291413:0xee1cfa646b638cf2!8m2!3d25.0899947!4d121.5242868!16s%2Fg%2F11jgtqlkqb!19sChIJExQpf2evQjQR8oxja2T6HO4?authuser=0&hl=zh-TW&rclk=1")

# # 等待頁面載入
# time.sleep(1)


# # 嘗試點擊「更多評論」
# try:
#     more_reviews_btn = WebDriverWait(driver, 10).until(
#         EC.element_to_be_clickable((By.XPATH, '//button[contains(@aria-label,"更多評論")]'))
#     )
#     more_reviews_btn.click()
#     print("點擊『更多評論』成功")
#     time.sleep(3)
# except Exception as e:
#     print("找不到『更多評論』", e)

# # 等待頁面載入
# time.sleep(1)

# def click_all_expand_buttons():
#     try:
#         while True:
#             # 找到所有「全文」按鈕
#             expand_buttons = driver.find_elements(By.XPATH, '//button[contains(@aria-label,"顯示更多")]')
#             print(f"找到 {len(expand_buttons)} 個『全文』按鈕")

#             if not expand_buttons:
#                 print("沒有更多『全文』按鈕")
#                 break

#             for i, button in enumerate(expand_buttons):
#                 try:
#                     # 滾動到按鈕位置，確保按鈕可見
#                     driver.execute_script("arguments[0].scrollIntoView(true);", button)
#                     time.sleep(0.5)  # 避免滾動過快
#                     button.click()
#                     print(f"點擊第 {i + 1} 個『全文』按鈕")
#                     time.sleep(0.5)  # 避免點擊過快
#                 except Exception as e:
#                     print(f"第 {i + 1} 個『全文』按鈕點擊失敗：{e}")
#                     continue

#             # 滾動評論區以加載更多評論
#             scrollable_div = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.XPATH, '//div[@aria-label="評論"]'))
#             )
#             driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
#             time.sleep(2)  # 等待評論加載
#     except Exception as e:
#         print("無法找『全文』按鈕：", e)


# click_all_expand_buttons()

# # 等待頁面載入
# time.sleep(1)

# # 抓評論
# reviews = driver.find_elements(By.XPATH, '//div[@data-review-id]')

# result = []

# seen = set()  # 用來檢查重複

# for review in reviews:
#     try:
#         author = review.find_element(By.XPATH, './/div[contains(@class,"d4r55 ")]').text
#         rating = review.find_element(By.XPATH, './/span[contains(@class,"kvMYJc")]').get_attribute("aria-label")

#         # 嘗試抓原文，如果抓不到才用翻譯版（避免拿到中文翻譯）
#         try:
#             text = review.find_element(By.XPATH, './/span[@jsname="bN97Pc"]').text  # 原文
#         except:
#             try:
#                 text = review.find_element(By.XPATH, './/span[contains(@class,"wiI7pd")]').text  # 翻譯
#             except:
#                 text = ""

#         # 判斷是否重複（作者 + 評論內容）
#         key = (author, text.strip())
#         if key in seen:
#             continue
#         seen.add(key)

#         result.append({
#             "author": author,
#             "rating": rating,
#             "text": text.strip()
#         })
#     except:
#         continue

# # 等待頁面載入
# time.sleep(1)

# driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
# time.sleep(5)  # 等待更長時間
    
# # 設定輸出檔案路徑
# output_path = os.path.join("Peter/Data/Comment/士林堃叔手作糯米腸.csv")

# # 儲存成 CSV
# with open(output_path, "w", encoding="utf-8", newline="") as f:
#     writer = csv.DictWriter(f, fieldnames=["author", "rating", "text"])  # 修正欄位名稱
#     writer.writeheader()
#     writer.writerows(result)  # 使用正確的變數名稱

# print(f"✅ 共抓到 {len(result)} 筆資料，已存到 {output_path}")

# driver.quit()
