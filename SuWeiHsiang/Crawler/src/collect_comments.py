from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

import pandas as pd
import os
import re
import time
from datetime import datetime,date
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
crawler_path = os.getenv("CRAWLER_PATH")

def check_load_new_data(driver,class_):
    req = driver.page_source
    soup = BeautifulSoup(req,'html.parser')
    return len(soup.find_all("div",class_=class_))

def create_driver():
    service = Service(executable_path=ChromeDriverManager().install())
    options = ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return Chrome(service=service, options=options)

def decide_wait_time(driver):
    comments_count = driver.find_element(By.XPATH,"//div[@class='F7nice ']/span[2]/span/span").get_attribute('aria-label').split()[0]
    comments_count = int(comments_count.replace(',',''))
    if comments_count > 4000 :
        return WebDriverWait(driver,60,0.1),comments_count
    elif comments_count > 3000 :
        return WebDriverWait(driver,50,0.1),comments_count
    elif comments_count > 2000 :
        return WebDriverWait(driver,40,0.1),comments_count
    if comments_count > 1000 :
        return WebDriverWait(driver,30,0.1),comments_count
    else :
        return WebDriverWait(driver,10,0.1),comments_count

def push_comment_button(driver,wait):
    wait.until(EC.element_to_be_clickable((By.XPATH,'//div[text()="評論"]')))
    driver.find_element(By.XPATH,'//div[text()="評論"]').click()

def get_scroll_page(driver,wait):
    wait.until(EC.presence_of_element_located((By.XPATH,"//div[@class='m6QErb DxyBCb kA9KIf dS8AEf XiKgde ']")))
    return driver.find_element(By.XPATH,"//div[@class='m6QErb DxyBCb kA9KIf dS8AEf XiKgde ']")

def sort_newest(driver,wait):
    wait.until(EC.element_to_be_clickable((By.XPATH,"//span[text()='排序']")))
    driver.find_element(By.XPATH,"//span[text()='排序']").click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="action-menu"]/div[2]')))
    driver.find_element(By.XPATH, '//*[@id="action-menu"]/div[2]').click()

def split_time_to_num_and_unit(customer):
    times = customer.find_element(By.CLASS_NAME,"rsqaWe").text
    time_num = int(re.search(r"\d+",times).group())
    time_unit = re.search(r"\D+",times).group().lstrip().rstrip("前")
    return time_num,time_unit

def comment_info(info_list,driver,customer,time_num,time_unit):
    info_list[0].append(customer.find_element(By.CLASS_NAME,"d4r55 ").text)
    tid = customer.find_element(By.CLASS_NAME,"al6Kxe").get_attribute("data-href")
    info_list[1].append(tid)
    try:
        info_list[2].append(customer.find_element(By.CLASS_NAME,"RfnDt ").text)
    except:
        info_list[2].append("")
    info_list[3].append(customer.find_element(By.CLASS_NAME,"kvMYJc").get_attribute('aria-label'))
    info_list[4].append(time_num)
    info_list[5].append(time_unit)
    try :
        id = customer.find_element(By.CLASS_NAME,"MyEned").get_attribute("id")
        try :
            driver.find_element(By.XPATH,f"//*[@id='{id}']/span[2]/button").click()
        except :
            pass
        comment = driver.find_element(By.XPATH,f"//*[@id='{id}']/span[1]")
        info_list[6].append(comment.text)
    except :
        info_list[6].append("")
    return info_list

def save_large_volumn_record(pre_count,dir,name):
    if pre_count >= 1000 and pre_count % 10 == 0 :
        path = Path(f"{crawler_path}/data/{dir}/large_volume.txt")
        with open(path,'a',encoding='utf-8-sig') as f:
                f.write(f"{datetime.now().replace(microsecond=0)} : ")
                f.write(f"爬取到{name}的第{pre_count}筆資料\n")
                f.close()

def create_dataframe(info_list,name):
    df = pd.DataFrame({"user_name":info_list[0],"user_id":info_list[1],"local_guide":info_list[2],"rating_stars":info_list[3],"time_num":info_list[4],"time_unit":info_list[5],"comment":info_list[6]})
    df.insert(0,"st_name",name)
    df["create_date"] = date.today()
    df["update_date"] = date.today()
    return df

def save_df_and_record(df,dir,name,comments_count):
    directory = Path(f"{crawler_path}/data/{dir}")
    directory.mkdir(parents=True,exist_ok=True)
    path = Path(f"{crawler_path}/data/{dir}/{dir}_comments.csv")
    if path.exists():
        df.to_csv(path,index=False,header=False,encoding='utf-8-sig',mode="a")
    else:
        df.to_csv(path,index=False,header=True,encoding='utf-8-sig',mode="a")
    df.info()
    with open(f"{crawler_path}/data/{dir}/record.txt",'a',encoding='utf-8-sig') as f:
        f.write(f"{datetime.now().replace(microsecond=0)} : ")
        f.write(f"{name}應有{comments_count}筆評論，實爬{df.shape[0]}筆資料\n")
        f.close()

def save_error_info(name,dir,start,count,e):
    print(f"爬取{name}時發生錯誤")
    path = Path(f"{crawler_path}/data/{dir}/log.txt")
    if not path.exists():
        path.touch()
    with open(path,"a",encoding='utf-8-sig') as f:
        f.write(f"{datetime.now().replace(microsecond=0)} : ")
        f.write(f"爬取編號{start + count}:{name}時發生錯誤\n{e}\n")
        f.close()

def collect_comments(name,url,dir) :
    # service = Service(f"{crawler_path}/src/chromedriver.exe")
    # options = ChromeOptions()

    # driver = Chrome(options = options,service = service)
    driver = create_driver()

    driver.get(url)
    wait,comments_count = decide_wait_time(driver)
    push_comment_button(driver,wait)
    page = get_scroll_page(driver,wait)
    sort_newest(driver,wait)
    user_name,user_id,local_guide,stars,times_num,times_unit,comments = [],[],[],[],[],[],[]
    info_list = [user_name,user_id,local_guide,stars,times_num,times_unit,comments]
    pre_count = 0
    while True :
        driver.execute_script("arguments[0].scrollTo(0,arguments[0].scrollHeight)",page)
        try :
            wait.until(lambda _ : pre_count < check_load_new_data(driver,"jftiEf fontBodyMedium"))
        except :
            print(f"已完成{name}評論搜尋")
            break
        customers = driver.find_elements(By.CLASS_NAME,"jJc9Ad ")
        for customer in customers[pre_count:] :
            time_num,time_unit = split_time_to_num_and_unit(customer)
            info_list = comment_info(info_list,driver,customer,time_num,time_unit)
        pre_count = check_load_new_data(driver,"jftiEf fontBodyMedium")
        print(f"在{name}爬取到{pre_count}則評論，進度{round(pre_count/comments_count*100)}%")
        save_large_volumn_record(pre_count,dir,name)

    df = create_dataframe(info_list,name)
    save_df_and_record(df,dir,name,comments_count)

    time.sleep(2)

    driver.close()

def collect_comments_by_range(dir,start,end):
    df = pd.read_csv(f"{crawler_path}/data/{dir}/{dir}_restaurant.csv")
    count = 1
    for name,link in zip(df.iloc[start:end,0],df.iloc[start:end,2]) :
        print(f"爬取第{start + count}家評價，尚餘{end - start - count}家待爬取")
        try :
            collect_comments(name,link,dir)
        except Exception as e:
            save_error_info(name,dir,start,count,e)
        time.sleep(1)
        count += 1

def collect_comments_by_list(dir,list):
    df = pd.read_csv(f"{crawler_path}/data/{dir}/{dir}_restaurant.csv")
    count = 1
    for i in list:
        name = df.iloc[i,0]
        link = df.iloc[i,2]
        print(f"爬取{name}評價，尚餘{len(list) - count}家待爬取")
        try :
            collect_comments(name,link,dir)
        except Exception as e:
            print(f"爬取{name}時發生錯誤")
            path = Path(f"{crawler_path}/data/{dir}/log.txt")
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
    start = 99                #要從第幾家開始蒐集評論(目前到樂華夜市第100家)
    end = 159                  #要從蒐集評論到第幾家
    #以上區域之參數請設定##
    # collect_comments_by_range(night_market,start,end)

    #需要補爬名單
    re_crawl = [98]
    collect_comments_by_list(night_market,re_crawl)