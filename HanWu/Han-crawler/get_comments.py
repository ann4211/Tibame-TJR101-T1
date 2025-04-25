from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
from pathlib import Path
import os

def check_load_new_data(driver,class_):
    req = driver.page_source
    soup = BeautifulSoup(req,'html.parser')
    return len(soup.find_all("div",class_=class_))

def collect_comments(name,url,output_dir,date_dir_name) :
    service = Service("C:\PythonLanguage\chromedriver-win64\chromedriver.exe")
    options = ChromeOptions()
    driver = Chrome(options = options,service = service)
    driver.get(url)
    comments_count = driver.find_element(By.XPATH,"//div[@class='F7nice ']/span[2]/span/span").get_attribute('aria-label').split()[0]
    comments_count = int(comments_count.replace(',',''))
    if comments_count > 4000 :
        wait = WebDriverWait(driver,60,0.1)
    elif comments_count > 3000 :
        wait = WebDriverWait(driver,50,0.1)
    elif comments_count > 2000 :
        wait = WebDriverWait(driver,40,0.1)
    if comments_count > 1000 :
        wait = WebDriverWait(driver,30,0.1)
    else :
        wait = WebDriverWait(driver,10,0.1)
    driver.find_element(By.XPATH,'//div[text()="評論"]').click()
    page = driver.find_element(By.XPATH,"//div[@class='m6QErb DxyBCb kA9KIf dS8AEf XiKgde ']")
    driver.find_element(By.XPATH,"//span[text()='排序']").click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="action-menu"]/div[2]')))
    driver.find_element(By.XPATH, '//*[@id="action-menu"]/div[2]').click()
    traveler = list()
    identity = list()
    times = list()
    stars = list()
    comments = list()
    pre_count = 0
    while True :
        driver.execute_script("arguments[0].scrollTo(0,arguments[0].scrollHeight)",page)
        try :
            wait.until(lambda _: pre_count < check_load_new_data(driver,"jftiEf fontBodyMedium"))
        except :
            print("已完成所有評論搜尋")
            break
        customers = driver.find_elements(By.CLASS_NAME,"jJc9Ad ")
        for customer in customers[pre_count:] :
            traveler.append(customer.find_element(By.CLASS_NAME,"d4r55 ").text)
            try:
                identity.append(customer.find_element(By.CLASS_NAME,"RfnDt ").text)
            except:
                identity.append("")
            times.append(customer.find_element(By.CLASS_NAME,"rsqaWe").text)
            stars.append(customer.find_element(By.CLASS_NAME,"kvMYJc").get_attribute('aria-label'))
            try :
                id = customer.find_element(By.CLASS_NAME,"MyEned").get_attribute("id")
                try :
                    driver.find_element(By.XPATH,f"//*[@id='{id}']/span[2]/button").click()
                except :
                    pass
                comment = driver.find_element(By.XPATH,f"//*[@id='{id}']/span[1]")
                comments.append(comment.text)
            except :
                comments.append("")
        pre_count = check_load_new_data(driver,"jftiEf fontBodyMedium")
    df = pd.DataFrame({"留言者":traveler,"留言者身分":identity,"留言時間":times,"星級評等":stars,"評論內容":comments})
    df.insert(0,"餐廳名稱",name,allow_duplicates=True)

    directory = os.path.join(output_dir, date_dir_name)
    os.makedirs(directory, exist_ok=True)  # 使用 exist_ok=True 避免重複創建資料夾的錯誤

    filepath = os.path.join(directory, f"{date_dir_name}_comments.csv")

    if os.path.exists(filepath):
        df.to_csv(filepath, index=False, header=False, encoding='utf-8-sig', mode="a")
    else:
        df.to_csv(filepath, index=False, header=True, encoding='utf-8-sig', mode="a")

    df.info()

    print(f"評論已保存到: {filepath}")
    time.sleep(2)
    driver.close()

def main():
    # 使用絕對路徑讀取餐廳CSV檔案
    csv_path = r"C:\tibame-t1\HanWu\Han-crawler\restaurants_list.csv"

    try:
        restaurants_df = pd.read_csv(csv_path)
        print(f"成功讀取餐廳數據，共 {len(restaurants_df)} 條記錄")
    except Exception as e:
        print(f"讀取餐廳CSV檔案失敗: {e}")
        return

    # 檢查CSV是否包含必要的列
    if '餐廳名稱' not in restaurants_df.columns or '餐廳連結' not in restaurants_df.columns:
        print("CSV檔案缺少必要的列: '餐廳名稱' 或 '餐廳連結'")
        print(f"CSV檔案現有的列: {list(restaurants_df.columns)}")
        return

    # 獲取包含 CSV 檔案的目錄
    csv_dir = os.path.dirname(os.path.abspath(csv_path))
    # 設置資料夾名稱
    date_dir_name = datetime.now().strftime("%Y%m%d")
    # 設置輸出資料夾的完整路徑
    output_data_dir = os.path.join(csv_dir, "data")
    # 創建主要的 data 資料夾（如果不存在）
    os.makedirs(output_data_dir, exist_ok=True)

    # 遍歷每個餐廳並爬取評論
    for idx, row in restaurants_df.iterrows():
        name = row['餐廳名稱']
        url = row['餐廳連結']

        print(f"開始處理第 {idx+1}/{len(restaurants_df)} 個餐廳: {name}")

        try:
            collect_comments(name, url, output_data_dir, date_dir_name)
            print(f"完成第 {idx+1}/{len(restaurants_df)} 個餐廳的爬取")
        except Exception as e:
            print(f"爬取餐廳 '{name}' 時發生錯誤: {e}")
            continue

        # 適當延遲，避免被封IP
        time.sleep(3)

    result_path = os.path.join(output_data_dir, date_dir_name, f"{date_dir_name}_comments.csv")
    print("所有餐廳評論爬取完成！")
    print(f"結果已保存到: {result_path}")

if __name__ == "__main__":
    main()