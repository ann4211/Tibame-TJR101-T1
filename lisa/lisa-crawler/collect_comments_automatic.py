from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from bs4 import BeautifulSoup
import pandas as pd

import time
from pathlib import Path

def check_load_new_data(driver,class_):
    req = driver.page_source
    soup = BeautifulSoup(req,'html.parser')
    return len(soup.find_all("div",class_=class_))

def collect_comments_automatic(name,url,night_market):
    driver = Chrome()

    driver.get(url)
    comments_count = driver.find_element(By.XPATH,"//div[@class='F7nice ']/span[2]/span/span").get_attribute('aria-label').split()[0]
    comments_count = int(comments_count.replace(',',''))
    if comments_count > 4000 :
        wait = WebDriverWait(driver,60,0.1)
    elif comments_count > 3000 :
        wait = WebDriverWait(driver,50,0.1)
    elif comments_count > 2000 :
        wait = WebDriverWait(driver,40,0.1)
    elif comments_count > 1000 :
        wait = WebDriverWait(driver,30,0.1)
    else :
        wait = WebDriverWait(driver,10,0.1)
    driver.find_element(By.XPATH,'//div[text()="評論"]').click()

    try:
        page = driver.find_element(By.XPATH, "//div[@class='m6QErb DxyBCb kA9KIf dS8AEf XiKgde ']")
    except NoSuchElementException:
        try:
            parent = driver.find_element(By.XPATH, "//div[@id='QA0Szd']")
            page = parent.find_element(By.XPATH, './div/div/div[1]/div[2]/div/div[1]/div/div/div[2]')
        except NoSuchElementException:
            print(f"{name}無法取得，跳過此頁")
            page = None

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
            wait.until(lambda _ : pre_count < check_load_new_data(driver,"jftiEf fontBodyMedium"))#WebDriverWait(driver, 等待的最長時間, 檢查條件的頻率, 忽略的例外類別).until(expected_conditions條件, 超時例外的錯誤訊息)
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
    directory = Path(f"./data/output/store_comment/{night_market}")
    directory.mkdir(parents=True,exist_ok=True)
    path = Path(f"./data/output/store_comment/{night_market}/20250425_crawler_nanjichang_rawdata_{night_market}_comments.csv")
    if path.exists():
        df.to_csv(path,index=False,header=False,encoding='utf-8-sig',mode="a")
    else:
        df.to_csv(path,index=False,header=True,encoding='utf-8-sig',mode="a")
    df.info()
    
    time.sleep(2)

    driver.close()

if __name__ == "__main__" :
    # "Dadong Night Market"
    night_markets =["Tainan Flower Night Market" , "Wusheng Night Market"]
    for night_market in night_markets:
        df = pd.read_csv(f"./data/output/store_list_address/{night_market}_check2.csv")

        count = 1
        for name, url in zip(df.iloc[ : ,0], df.iloc[ : ,2]):
            print(f"爬取{night_market}的第{count}家評價，尚餘{len(df) - count}家待爬取")
            try :
                collect_comments_automatic(name,url,night_market)
            except Exception as e:
                print(f"爬取{name}時發生錯誤")
                path = Path(f"./data/output/store_comment/exception/")
                path.mkdir(parents=True,exist_ok=True)
                file = Path(f"./data/output/store_comment/exception/{night_market}.txt")
                with open(file,"a",encoding='utf-8-sig') as f:
                    f.write(f"爬取{name}時發生錯誤\n{e}\n")

            time.sleep(1)
            count += 1