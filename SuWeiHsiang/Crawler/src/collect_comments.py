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

def check_load_new_data(driver,class_):
    req = driver.page_source
    soup = BeautifulSoup(req,'html.parser')
    return len(soup.find_all("div",class_=class_))

def collect_comments(name,url,dir) :
    service = Service("./src/chromedriver.exe")
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
        if pre_count >= 1000 and pre_count % 10 == 0 :
            path = Path(f"./data/{dir}/large_volume.txt")
            with open(path,'a',encoding='utf-8-sig') as f:
                    f.write(f"{datetime.now().replace(microsecond=0)} : ")
                    f.write(f"爬取到{name}的第{pre_count}筆資料\n")
                    f.close()

    df = pd.DataFrame({"留言者":traveler,"留言者身分":identity,"留言時間":times,"星級評等":stars,"評論內容":comments})
    df.insert(0,"餐廳名稱",name,allow_duplicates=True)
    directory = Path(f"./data/{dir}")
    directory.mkdir(parents=True,exist_ok=True)
    path = Path(f"./data/{dir}/{dir}_comments.csv")
    if path.exists():
        df.to_csv(path,index=False,header=False,encoding='utf-8-sig',mode="a")
    else:
        df.to_csv(path,index=False,header=True,encoding='utf-8-sig',mode="a")
    df.info()
    with open(f"./data/{dir}/record.txt",'a',encoding='utf-8-sig') as f:
        f.write(f"{datetime.now().replace(microsecond=0)} : ")
        f.write(f"{name}應有{comments_count}筆評論，實爬{df.shape[0]}筆資料\n")
        f.close()
    
    time.sleep(2)

    driver.close()

def collect_comments_by_range(dir,start,end):
    df = pd.read_csv(f"./data/{dir}/restaurant_around_corner.csv")
    count = 1
    for name,link in zip(df.iloc[start:end,0],df.iloc[start:end,2]) :
        print(f"爬取第{start + count}家評價，尚餘{end - start - count}家待爬取")
        try :
            collect_comments(name,link,dir)
        except Exception as e:
            print(f"爬取{name}時發生錯誤")
            path = Path(f"./data/{dir}/log.txt")
            if not path.exists():
                path.touch()
            with open(path,"a",encoding='utf-8-sig') as f:
                f.write(f"{datetime.now().replace(microsecond=0)} : ")
                f.write(f"爬取編號{start + count}:{name}時發生錯誤\n{e}\n")
                f.close()
        time.sleep(1)
        count += 1

def collect_comments_by_list(dir,list):
    df = pd.read_csv(f"./data/{dir}/restaurant_around_corner.csv")
    count = 1
    for i in list:
        name = df.iloc[i,0]
        link = df.iloc[i,2]
        print(f"爬取{name}評價，尚餘{len(list) - count}家待爬取")
        try :
            collect_comments(name,link,dir)
        except Exception as e:
            print(f"爬取{name}時發生錯誤")
            path = Path(f"./data/{dir}/log.txt")
            if not path.exists():
                path.touch()
            with open(path,"a",encoding='utf-8-sig') as f:
                f.write(f"{datetime.now().replace(microsecond=0)} : ")
                f.write(f"爬取{name}時發生錯誤\n{e}\n")
                f.close()
        time.sleep(1)
        count += 1

if __name__ == "__main__" :
    #以下區域之參數請設定##
    night_market = "NingXia"     #設定要爬取的區域
    typename = "小吃"          #店家的類型(如小吃、餐廳等等)
    start = 163                #要從第幾家開始蒐集評論(目前到樂華夜市第100家)
    end = 164                  #要從蒐集評論到第幾家
    #以上區域之參數請設定##
    # collect_comments_by_range(night_market,start,end)

    #需要補爬名單
    re_crawl = [154]
    collect_comments_by_list(night_market,re_crawl)
    
    #大量留言補爬名單
    # Lehua_crawl = [12,15,30,31,39,52,68,74,82]
    #NingXia_crawl = [2,6,8,142]
    # re_crawl = [6]
    # collect_comments_by_list(night_market,re_crawl)

    
    #測試區
    # num = df.iloc[12,0]
    # link = df.iloc[12,1]
    # collect_comments(num,link,night_market)

    #需要爬留言者名字
    #客多美咖啡再檢視看看
    #把想要的餐廳類型都抓下來
    #不刪除重複留言
    #沒有留言就刪除