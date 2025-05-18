import os
import re
import time
from pathlib import Path
from random import uniform
from typing import Optional, Tuple, List

import pandas as pd
from pandas import DataFrame
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from geopy.distance import geodesic
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()
crawler_path = os.getenv("CRAWLER_PATH")  # 爬蟲相關檔案所在資料夾


def create_driver() -> Chrome:
    """
    建立爬蟲driver
    """
    service = Service(executable_path=ChromeDriverManager().install())
    options = ChromeOptions()
    options.add_argument("--headless")  # 無頭模式
    options.add_argument("--disable-gpu")  # 停用GPU
    options.add_argument("--disable-extensions")  # 停用擴充套件
    options.add_argument("--disable-infobars")  # 移除提示條
    options.add_argument("--start-maximized")  # 視窗最大化
    options.add_argument("--disable-notifications")  # 阻止視窗跳出通知提示
    options.add_argument("--no-sandbox")  # 關閉沙盒模式
    options.add_argument("--disable-dev-shm-usage")  # 禁用共享記憶體作為暫存區
    return Chrome(service=service, options=options)


def decide_wait_time(driver: Chrome) -> WebDriverWait:
    """
    設定等待時間
    """
    return WebDriverWait(driver, 10, 0.1)


def get_scroll_page(driver: Chrome, wait: WebDriverWait) -> WebElement:
    """
    取得滑動頁面的WebElement
    """
    wait.until(EC.presence_of_element_located((By.XPATH, "//*[@role='feed']")))
    return driver.find_element(By.XPATH, "//*[@role='feed']")


def save_restaurant_link_to_csv(dir: str, soup: BeautifulSoup) -> None:
    """
    存店家名稱及連結為csv檔
    """
    names, links = [], []
    restaurants = soup.select("div.Nv2PK")
    for restaurant in restaurants:
        info = restaurant.find("a")
        names.append(info["aria-label"])
        links.append(info["href"])
    df = pd.DataFrame({"餐廳名稱": names, "餐廳連結": links})
    path = Path(f"{crawler_path}/data/{dir}")
    path.mkdir(parents=True, exist_ok=True)
    df.to_csv(
        f"{crawler_path}/data/{dir}/restaurants.csv",
        index=False,
        header=True,
        encoding="utf-8-sig",
    )
    df.info()


def send_info_to_search_box(driver: Chrome, st_name: str, nm_name: str) -> None:
    """
    在搜尋框中輸入店家名稱及所在夜市名
    """
    driver.find_element(
        By.XPATH, '//input[@class="fontBodyMedium searchboxinput xiQnY "]'
    ).send_keys(st_name + " " + nm_name)  # 在搜尋框中輸入店家名稱及夜市名稱
    driver.find_element(
        By.XPATH, '//input[@class="fontBodyMedium searchboxinput xiQnY "]'
    ).send_keys(Keys.ENTER)  # 點擊查詢


def check_abs_locate_stab(driver: Chrome, wait_time: float) -> Optional[str]:
    """
    等google map位置就定位
    """
    start = time.time()
    curr_url = driver.current_url
    while True:
        time.sleep(1)
        if (
            curr_url == driver.current_url and "@" in curr_url
        ):  # 如果網址不再變動則視為已就定位
            return curr_url
        elif (
            "@" not in curr_url and time.time() - start > wait_time
        ):  # 如果等待時間超過容許時間且尚未出現經緯度位置
            return None
        else:  # 尚未就定位
            curr_url = driver.current_url


def put_abs_locate_to_list(driver: Chrome, latitudes: float, longitudes: float) -> None:
    """
    將經緯度放入list
    """
    curr_url = check_abs_locate_stab(driver, 10)
    if curr_url is not None:
        lati_pattern = r"\d{2}\.\d+"
        long_pattern = r"\d{3}\.\d+"
        latitude = re.search(lati_pattern, curr_url).group()
        longtitude = re.search(long_pattern, curr_url).group()

        latitudes.append(latitude)
        longitudes.append(longtitude)
    else:
        latitudes.append("")
        longitudes.append("")


def save_abs_locate_to_csv(
    df: DataFrame, dir: str, latitudes: float, longitudes: float
) -> None:
    """
    儲存絕對路徑相關資訊
    """
    df["latitude"] = latitudes
    df["longitude"] = longitudes
    path = Path(f"{crawler_path}/data/{dir}")
    path.mkdir(parents=True, exist_ok=True)
    df.to_csv(
        f"{path}/with_abs_locate.csv", header=True, index=False, encoding="utf-8-sig"
    )


def restaurant_info(driver: Chrome, info_list: List[List[str]]) -> None:
    """
    儲存店家資訊至list(分別為地址、星級、均消、評論總數、評論標籤)
    """
    try:
        info_list[0].append(
            driver.find_element(By.CLASS_NAME, "CsEnBe")
            .get_attribute("aria-label")
            .lstrip("地址: ")
        )
    except Exception:
        info_list[0].append("")
    try:
        info_list[1].append(
            driver.find_element(By.CLASS_NAME, "ceNzKf")
            .get_attribute("aria-label")
            .rstrip(" 顆星")
        )
    except Exception:
        info_list[1].append("")
    try:
        info_list[2].append(
            driver.find_element(By.XPATH, "//div[@class='F7nice ']/span[2]/span/span")
            .text.lstrip("(")
            .rstrip(")")
            .replace(",", "")
        )
    except Exception:
        info_list[2].append("")
    try:
        info_list[3].append(
            driver.find_element(
                By.XPATH, "//span[@class='mgr77e']/span/span[2]/span/span"
            ).text
        )
    except Exception:
        info_list[3].append("")
    try:
        tag_lst = driver.find_elements(
            By.XPATH, "//button[contains(@aria-label, '則評論提到')]"
        )
        info_list[4].append(
            [tag.get_attribute("aria-label").split("提到")[1] for tag in tag_lst]
        )
    except Exception:
        info_list[4].append("")


def save_restaurant_info_to_csv(
    df: DataFrame, dir: str, info_list: List[List[str]]
) -> None:
    """
    儲存完整店家資訊
    """
    df.insert(1, "st_address", info_list[0])
    df["st_score"] = info_list[1]  # 星級
    df["st_price"] = info_list[2]  # 均消
    df["st_total_com"] = info_list[3]  # 評論總數
    df["st_tag"] = info_list[4]  # 評論標籤
    path = Path(f"{crawler_path}/data/{dir}")
    path.mkdir(parents=True, exist_ok=True)
    df.to_csv(
        f"{path}/{dir}_restaurant.csv", header=True, index=False, encoding="utf-8-sig"
    )


def collect_links(district: str, typename: str, dir: str) -> None:
    """
    蒐集店家名稱及連結
    """
    driver = create_driver()

    base_url = "https://www.google.com/maps/search/"
    url = base_url + district + "+" + typename

    driver.get(url)
    wait = decide_wait_time(driver)
    page = get_scroll_page(driver, wait)
    while True:
        req = driver.page_source
        soup = BeautifulSoup(req, "html.parser")
        if soup.select_one("span.HlvSq") is None:  # 尚未獲得所有店家
            driver.execute_script(
                "arguments[0].scrollTo(0,arguments[0].scrollHeight)", page
            )
            time.sleep(uniform(1, 2))
        else:  # 已獲得所有店家
            break

    save_restaurant_link_to_csv(dir, soup)

    driver.close()


def get_abs_locate(path: str, nm_name: str, dir: str) -> None:
    """
    獲得店家之經緯度
    """
    df = pd.read_csv(path)

    latitudes, longitudes = [], []
    url = "https://www.google.com/maps/"
    for i in range(df.shape[0]):
        name = df.iloc[i, 0]

        driver = create_driver()
        driver.get(url)
        send_info_to_search_box(driver, name, nm_name)
        put_abs_locate_to_list(driver, latitudes, longitudes)
        driver.close()

    save_abs_locate_to_csv(df, dir, latitudes, longitudes)


def get_distance(
    abs_locate: Tuple[float, float], target_locate: Tuple[float, float]
) -> float:
    """
    計算店家經緯度與夜市經緯度距離
    """
    return geodesic(abs_locate, target_locate).km


def with_dist(
    path: str, target_latitude: float, target_longitude: float, dir: str
) -> None:
    """
    店家資料檔案加上店家之經緯度與夜市經緯度距離
    """
    df = pd.read_csv(path)
    distance = list()
    for i in range(df.shape[0]):
        latitude = df.iloc[i, 2]
        longitude = df.iloc[i, 3]
        abs_locate = f"{latitude},{longitude}"
        try:
            distance.append(
                get_distance((abs_locate), (target_latitude, target_longitude))
            )
        except Exception:
            distance.append(10000)
    df["distance"] = distance
    path = Path(f"{crawler_path}/data/{dir}")
    path.mkdir(parents=True, exist_ok=True)
    df.to_csv(f"{path}/with_dist.csv", index=False, header=True, encoding="utf-8-sig")


def drop_faraway(path: str, dir: str, dist: float) -> None:
    """
    只留下距離夜市一定距離之店家
    """
    df = pd.read_csv(path)
    df.drop(df[df["distance"] > dist].index, inplace=True)
    path = Path(f"{crawler_path}/data/{dir}")
    path.mkdir(parents=True, exist_ok=True)
    df.to_csv(
        f"{path}/restaurant_around_corner.csv",
        index=False,
        header=True,
        encoding="utf-8-sig",
    )


def faraway_restaurants(path: str, dir: str, dist: float) -> None:
    """
    另存距離夜市比較遠的店家
    """
    df = pd.read_csv(path)
    df.drop(df[df["distance"] <= dist].index, inplace=True)
    path = Path(f"{crawler_path}/data/{dir}")
    path.mkdir(parents=True, exist_ok=True)
    df.to_csv(
        f"{path}/restaurant_faraway.csv", index=False, header=True, encoding="utf-8-sig"
    )


def get_restaurant_info(path: str, dir: str) -> None:
    """
    爬取店家相關資訊並儲存成csv檔
    """
    df = pd.read_csv(path)

    driver = create_driver()  # 建立爬蟲driver

    site, stars, expense, comments, tags = [], [], [], [], []
    info_list = [site, stars, expense, comments, tags]
    for i in range(df.shape[0]):
        url = df.iloc[i, 1]
        driver.get(url)
        restaurant_info(driver, info_list)

    driver.close()

    save_restaurant_info_to_csv(df, dir, info_list)
