import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from random import uniform
import time
from geopy.distance import geodesic
from pathlib import Path
import re

def check_load_new_data(driver,class_):
    req = driver.page_source
    soup = BeautifulSoup(req,'html.parser')
    return len(soup.find_all("div",class_=class_))

def collect_links(district,typename,dir) :
    service = Service("C:\PythonLanguage\chromedriver-win64\chromedriver.exe")
    options = ChromeOptions()

    driver = Chrome(options = options,service = service)

    base_url = "https://www.google.com/maps/search/"

    url = base_url + district + "+" + typename

    driver.get(url)
    page = driver.find_element(By.XPATH,"//*[@role='feed']")
    while True :
        req = driver.page_source
        soup = BeautifulSoup(req,'html.parser')
        if soup.select_one("span.HlvSq") == None :
            driver.execute_script("arguments[0].scrollTo(0,arguments[0].scrollHeight)",page)
            time.sleep(uniform(1,2))
        else :
            break

    names = list()
    links = list()
    restaurants = soup.select("div.Nv2PK")
    for restaurant in restaurants :
        info = restaurant.find('a')
        names.append(info['aria-label'])
        links.append(info['href'])
    df = pd.DataFrame({"餐廳名稱":names,"餐廳連結":links})
    path = Path(f"data/{dir}")
    path.mkdir(parents=True,exist_ok=True)
    df.to_csv(f"data/{dir}/restaurants.csv",index=False,header=True,encoding='utf-8-sig')
    df.info()

    time.sleep(2)

    driver.close()

def get_abs_locate(path,night_market_name,dir):#加上經緯度的函式
    df = pd.read_csv(path)

    service = Service("C:\PythonLanguage\chromedriver-win64\chromedriver.exe")
    options = ChromeOptions()

    latitudes = list()
    longitudes = list()
    url = 'https://www.google.com/maps/'
    for i in range(df.shape[0]):
        name = df.iloc[i,0]

        driver = Chrome(options = options,service = service)
        driver.get(url)
        time.sleep(1)
        driver.find_element(By.XPATH,'//input[@class="fontBodyMedium searchboxinput xiQnY "]').send_keys(name+" "+night_market_name)
        time.sleep(1)
        driver.find_element(By.XPATH,'//input[@class="fontBodyMedium searchboxinput xiQnY "]').send_keys(Keys.ENTER)

        time.sleep(6)#等待時間可以調高，或是可以有更好的寫法，目標是讓絕對位置完全呈現
        current_url = driver.current_url
        lati_pattern = r'\d{2}\.\d+'
        long_pattern = r'\d{3}\.\d+'
        latitude = re.search(lati_pattern,current_url).group()
        longtitude = re.search(long_pattern,current_url).group()
        
        latitudes.append(latitude)
        longitudes.append(longtitude)
        driver.close()

    df['latitude'] = latitudes
    df['longitude'] = longitudes
    path = Path(f"data/{dir}")
    path.mkdir(parents=True,exist_ok=True)
    df.to_csv(f"{path}/with_abs_locate.csv",header=True,index=False,encoding='utf-8-sig')

def get_distance(abs_locate,target_locate):#店家經緯度與夜市經緯度距離
    return geodesic(abs_locate,target_locate).km

def with_dist(path,target_latitude,target_longitude,dir):#加上店家之經緯度與夜市經緯度距離
    df = pd.read_csv(path)
    distance = list()
    for i in range(df.shape[0]):
        latitude = df.iloc[i,2]
        longitude = df.iloc[i,3]
        abs_locate = f"{latitude},{longitude}"
        distance.append(get_distance((abs_locate),(target_latitude,target_longitude)))
    df['distance'] = distance
    path = Path(f"data/{dir}")
    path.mkdir(parents=True,exist_ok=True)
    df.to_csv(f'{path}/with_dist.csv',index=False,header=True,encoding='utf-8-sig')

def drop_faraway(path,dist,dir):#只留下距離夜市一定距離之店家(因為有些店家或許根本不在夜市裡)
    df = pd.read_csv(path)
    df.drop(df[df['distance'] > dist].index,inplace=True)
    path = Path(f"data/{dir}")
    path.mkdir(parents=True,exist_ok=True)
    df.to_csv(f"{path}/restaurant_around_corner.csv",index=False,header=True,encoding='utf-8-sig')

def faraway_restaurants(path,dist,dir):#那些距離夜市比較遠的店家，可以再確認是否有誤刪的店家
    df = pd.read_csv(path)
    df.drop(df[df['distance'] <= dist].index,inplace=True)
    path = Path(f"data/{dir}")
    path.mkdir(parents=True,exist_ok=True)
    df.to_csv(f"{path}/restaurant_faraway.csv",index=False,header=True,encoding='utf-8-sig')


if __name__ == "__main__" :
    ###########以下請設定###########
    chinese_nightmarket = "逢甲夜市"   #店家的中文名稱(作為Google地圖搜尋關鍵字)
    typename = "日本餐廳"                 #店家的類型(如小吃、餐廳等等)
    nightmarket = "FengChia"             #店家的英文名稱(為了創建檔案存取資料夾用)
    target_latitude = 24.1775449       #店家的緯度
    target_longitude = 120.6460099    #店家的經度
    distance = 0.5                   #店家與夜市的距離(方圓幾公里內的店家才可以算是在夜市裡)
    ###########以上請設定###########
    collect_links(chinese_nightmarket,typename,nightmarket)
    get_abs_locate(f'data/{nightmarket}//restaurants.csv',chinese_nightmarket,nightmarket)
    with_dist(f"data/{nightmarket}/with_abs_locate.csv",target_latitude,target_longitude,nightmarket)
    drop_faraway(f"data/{nightmarket}/with_dist.csv",distance,nightmarket)
    faraway_restaurants(f"data/{nightmarket}/with_dist.csv",distance,nightmarket)