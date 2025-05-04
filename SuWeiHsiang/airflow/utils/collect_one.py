from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from utils.load_count import check_load_count

import pandas as pd
import re
import time
from datetime import datetime,date
from pathlib import Path

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

def is_crawler_stop(time_num,time_unit):
    if ("天" in time_unit  and time_num > 1) or any(unit in time_unit for unit in ("週", "月", "年")) :
        return True

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

def create_dataframe(info_list,name):
    df = pd.DataFrame({"user_name":info_list[0],"user_id":info_list[1],"local_guide":info_list[2],"rating_stars":info_list[3],"time_num":info_list[4],"time_unit":info_list[5],"comment":info_list[6]})
    df.insert(0,"st_name",name)
    df["create_date"] = date.today()
    df["update_date"] = date.today()
    return df

def save_df_and_record(df,name):
    directory = Path("./data/Crawler")
    directory.mkdir(parents=True,exist_ok=True)
    path = Path(f"{directory}/comments.csv")
    if path.exists():
        df.to_csv(path,index=False,header=False,encoding='utf-8-sig',mode="a")
    else:
        df.to_csv(path,index=False,header=True,encoding='utf-8-sig',mode="a")
    df.info()
    with open(f"{directory}/record.txt",'a',encoding='utf-8-sig') as f:
        f.write(f"{datetime.now().replace(microsecond=0)} : ")
        f.write(f"{name}爬取到{df.shape[0]}筆新評論\n")
        f.close()

def one_restaurant_comments(name,url):
    driver = create_driver()

    driver.get(url)
    wait = WebDriverWait(driver,10,0.1)
    push_comment_button(driver,wait)
    page = get_scroll_page(driver,wait)
    sort_newest(driver,wait)
    user_name,user_id,local_guide,stars,times_num,times_unit,comments = [],[],[],[],[],[],[]
    info_list = [user_name,user_id,local_guide,stars,times_num,times_unit,comments]
    pre_count = 0
    crawler_stop = False
    while True :
        driver.execute_script("arguments[0].scrollTo(0,arguments[0].scrollHeight)",page)
        try :
            wait.until(lambda _ : pre_count < check_load_count(driver,"jftiEf fontBodyMedium"))
        except :
            print(f"已完成{name}評論搜尋")
            break
        customers = driver.find_elements(By.CLASS_NAME,"jJc9Ad ")
        for customer in customers[pre_count:] :
            time_num,time_unit = split_time_to_num_and_unit(customer)
            crawler_stop =  is_crawler_stop(time_num,time_unit)
            if crawler_stop:
                break
            info_list = comment_info(info_list,driver,customer,time_num,time_unit)
        pre_count = check_load_count(driver,"jftiEf fontBodyMedium")
        print(f"正在{name}搜尋{pre_count}則評論中是否有新評論")
        if crawler_stop:
            break

    df = create_dataframe(info_list,name)
    save_df_and_record(df,name)

    driver.close()
    time.sleep(5)