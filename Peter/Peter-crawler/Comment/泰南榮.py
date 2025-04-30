# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time, os, csv

# # 設定 Chrome 選項
# chrome_options = Options()
# chrome_options.add_argument("--headless")  # 除錯時建議先不要加
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--window-size=1920,1080")

# driver = webdriver.Chrome(options=chrome_options)

# # 開啟 Google Maps 商家頁面
# driver.get("https://www.google.com.tw/maps/place/%E6%B3%B0%E5%8D%97%E6%A6%AE%EF%BD%9C%E5%A3%AB%E6%9E%97%E5%A4%9C%E5%B8%82%EF%BD%9C%E6%B3%B0%E5%BC%8F%E7%BE%8E%E9%A3%9F%EF%BD%9C%E6%9D%B1%E5%8D%97%E4%BA%9E%E7%BE%8E%E9%A3%9F%EF%BD%9C%E9%8A%98%E5%82%B3%E5%A4%A7%E5%AD%B8%EF%BD%9C%E6%89%93%E6%8B%8B%E8%B1%AC%E8%82%89%E9%A3%AF%EF%BD%9C%E6%B3%B0%E5%BC%8F%E7%B6%A0%E5%92%96%E5%93%A9%EF%BD%9C%E8%9D%A6%E4%BB%81%E7%82%92%E9%A3%AF/@25.0879944,121.526669,682m/data=!3m2!1e3!4b1!4m6!3m5!1s0x3442af2af07eb3a1:0x1878a4c0963d19f8!8m2!3d25.0879944!4d121.526669!16s%2Fg%2F11sb5k3ssw?authuser=0&hl=zh-TW&entry=ttu&g_ep=EgoyMDI1MDQyNy4xIKXMDSoASAFQAw%3D%3D")

# # 等待頁面載入
# time.sleep(2)


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




# def click_all_expand_buttons():
#     try:
#         expand_buttons = driver.find_elements(By.XPATH, '//button[contains(@aria-label,"顯示更多")]')
#         print(f"找到 {len(expand_buttons)} 個『全文』按鈕")

#         for i, button in enumerate(expand_buttons):
#             try:
#                 driver.execute_script("arguments[0].scrollIntoView(true);", button)
#                 time.sleep(1)
#                 button.click()
#                 print(f"點擊第 {i+1} 個『全文』")
#                 time.sleep(1)
#             except Exception as e:
#                 print(f"點擊第 {i+1} 失敗：{e}")
#     except Exception as e:
#         print("無法找『全文』按鈕：", e)

# click_all_expand_buttons()



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


    


# # 設定輸出檔案路徑
# output_path = os.path.join("Peter/Data/Comment/泰南榮.csv")

# # 儲存成 CSV
# with open(output_path, "w", encoding="utf-8", newline="") as f:
#     writer = csv.DictWriter(f, fieldnames=["author", "rating", "text"])  # 修正欄位名稱
#     writer.writeheader()
#     writer.writerows(result)  # 使用正確的變數名稱

# print(f"✅ 共抓到 {len(result)} 筆資料，已存到 {output_path}")

# driver.quit()
