import os
import re
import time
from typing import Tuple, List
from datetime import date, datetime
from pathlib import Path

import pandas as pd
from pandas import DataFrame
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()
crawler_path = os.getenv("CRAWLER_PATH")  # 爬蟲相關檔案所在資料夾


def check_load_new_data(driver: Chrome, class_: str) -> int:
    """
    目前所在動態頁面之評論資料筆數
    """
    req = driver.page_source
    soup = BeautifulSoup(req, "html.parser")
    return len(soup.find_all("div", class_=class_))


def create_driver() -> Chrome:
    """
    建立爬蟲driver
    """
    service = Service(executable_path=ChromeDriverManager().install())
    options = ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return Chrome(service=service, options=options)


def decide_wait_time(driver: Chrome) -> Tuple[WebDriverWait, int]:
    """
    依照店家評論總數決定等待時間
    """
    comments_count = (
        driver.find_element(By.XPATH, "//div[@class='F7nice ']/span[2]/span/span")
        .get_attribute("aria-label")
        .split()[0]
    )
    comments_count = int(comments_count.replace(",", ""))
    if comments_count > 4000:
        return WebDriverWait(driver, 60, 0.1), comments_count
    elif comments_count > 3000:
        return WebDriverWait(driver, 50, 0.1), comments_count
    elif comments_count > 2000:
        return WebDriverWait(driver, 40, 0.1), comments_count
    if comments_count > 1000:
        return WebDriverWait(driver, 30, 0.1), comments_count
    else:
        return WebDriverWait(driver, 10, 0.1), comments_count


def push_comment_button(driver: Chrome, wait: WebDriverWait) -> None:
    """
    點擊「評論」標籤
    """
    wait.until(EC.element_to_be_clickable((By.XPATH, '//div[text()="評論"]')))
    driver.find_element(By.XPATH, '//div[text()="評論"]').click()


def get_scroll_page(driver: Chrome, wait: WebDriverWait) -> WebElement:
    """
    取得滑動頁面的WebElement
    """
    wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//div[@class='m6QErb DxyBCb kA9KIf dS8AEf XiKgde ']")
        )
    )
    return driver.find_element(
        By.XPATH, "//div[@class='m6QErb DxyBCb kA9KIf dS8AEf XiKgde ']"
    )


def sort_newest(driver: Chrome, wait: WebDriverWait) -> None:
    """
    選按「最新」之評論排列方式
    """
    wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='排序']")))
    driver.find_element(By.XPATH, "//span[text()='排序']").click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="action-menu"]/div[2]')))
    driver.find_element(By.XPATH, '//*[@id="action-menu"]/div[2]').click()


def split_time_to_num_and_unit(customer: WebElement) -> Tuple[int, str]:
    """
    將評論時間拆分為時間值與時間單位
    """
    times = customer.find_element(By.CLASS_NAME, "rsqaWe").text
    time_num = int(re.search(r"\d+", times).group())
    time_unit = re.search(r"\D+", times).group().lstrip().rstrip("前")
    return time_num, time_unit


def comment_info(
    info_list: List[List[str]],
    driver: Chrome,
    customer: WebElement,
    time_num: int,
    time_unit: str,
) -> List[List[str]]:
    """
    蒐集評論相關資訊
    """
    info_list[0].append(customer.find_element(By.CLASS_NAME, "d4r55 ").text)
    tid = customer.find_element(By.CLASS_NAME, "al6Kxe").get_attribute("data-href")
    info_list[1].append(tid)
    try:
        info_list[2].append(customer.find_element(By.CLASS_NAME, "RfnDt ").text)
    except Exception:
        info_list[2].append("")
    info_list[3].append(
        customer.find_element(By.CLASS_NAME, "kvMYJc").get_attribute("aria-label")
    )
    info_list[4].append(time_num)
    info_list[5].append(time_unit)
    try:
        id = customer.find_element(By.CLASS_NAME, "MyEned").get_attribute("id")
        try:
            driver.find_element(By.XPATH, f"//*[@id='{id}']/span[2]/button").click()
        except Exception:
            pass
        comment = driver.find_element(By.XPATH, f"//*[@id='{id}']/span[1]")
        info_list[6].append(comment.text)
    except Exception:
        info_list[6].append("")
    return info_list  # list依序為評論者姓名、評論者ID、在地嚮導標籤、評論星等、評論時間值、評論時間單位、評論內容


def save_large_volumn_record(pre_count: int, dir: str, name: str) -> None:
    """
    觀察評論總數超過1000則評論之店家每滑動一次須等待之時間
    """
    if pre_count >= 1000 and pre_count % 10 == 0:
        path = Path(f"{crawler_path}/data/{dir}/large_volume.txt")
        with open(path, "a", encoding="utf-8-sig") as f:
            f.write(f"{datetime.now().replace(microsecond=0)} : ")
            f.write(f"爬取到{name}的第{pre_count}筆資料\n")
            f.close()


def create_dataframe(info_list: List[List[str]], name: str) -> DataFrame:
    """
    建立dataframe存取爬取到的資訊
    """
    df = pd.DataFrame(
        {
            "user_name": info_list[0],
            "user_id": info_list[1],
            "local_guide": info_list[2],
            "rating_stars": info_list[3],
            "time_num": info_list[4],
            "time_unit": info_list[5],
            "comment": info_list[6],
        }
    )
    df.insert(0, "st_name", name)  # 在第一欄插入店家名稱
    df["create_date"] = date.today()  # 設定創建檔案日期
    df["update_date"] = date.today()  # 設定更新檔案日期
    return df


def save_df_and_record(df: DataFrame, dir: str, name: str, comments_count: int) -> None:
    """
    儲存自該店家蒐集到的評論，並且記錄蒐集評論之情形
    """
    directory = Path(f"{crawler_path}/data/{dir}")
    directory.mkdir(parents=True, exist_ok=True)
    path = Path(f"{crawler_path}/data/{dir}/{dir}_comments.csv")  # 夜市評論存檔路徑
    if path.exists():  # 若該檔案已存在則無需重複header
        df.to_csv(path, index=False, header=False, encoding="utf-8-sig", mode="a")
    else:
        df.to_csv(path, index=False, header=True, encoding="utf-8-sig", mode="a")
    df.info()
    with open(f"{crawler_path}/data/{dir}/record.txt", "a", encoding="utf-8-sig") as f:
        f.write(f"{datetime.now().replace(microsecond=0)} : ")
        f.write(f"{name}應有{comments_count}筆評論，實爬{df.shape[0]}筆資料\n")
        f.close()


def save_error_info(
    name: str, dir: str, start: int, count: int, e: BaseException
) -> None:
    """
    發生錯誤時存取錯誤紀錄
    """
    print(f"爬取{name}時發生錯誤")
    path = Path(f"{crawler_path}/data/{dir}/log.txt")  # 存取錯誤紀錄的log檔
    if not path.exists():  # 尚未有檔案則先建立
        path.touch()
    with open(path, "a", encoding="utf-8-sig") as f:
        f.write(f"{datetime.now().replace(microsecond=0)} : ")
        f.write(f"爬取編號{start + count}:{name}時發生錯誤\n{e}\n")
        f.close()


def collect_comments(name: str, url: str, dir: str) -> None:
    """
    蒐集店家評論，
    參數為店家名稱、店家google map連結、店家所在夜市
    """
    driver = create_driver()

    driver.get(url)
    wait, comments_count = decide_wait_time(driver)
    push_comment_button(driver, wait)
    page = get_scroll_page(driver, wait)
    sort_newest(driver, wait)
    user_name, user_id, local_guide, stars, times_num, times_unit, comments = (
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    )
    info_list = [
        user_name,
        user_id,
        local_guide,
        stars,
        times_num,
        times_unit,
        comments,
    ]
    pre_count = 0
    while True:
        driver.execute_script(
            "arguments[0].scrollTo(0,arguments[0].scrollHeight)", page
        )
        try:
            wait.until(
                lambda _: pre_count
                < check_load_new_data(driver, "jftiEf fontBodyMedium")
            )  # 等待滑動頁面後是否有新評論載入
        except Exception:
            print(
                f"已完成{name}評論搜尋"
            )  # 若滑動前後評論總數相同則視為已爬取所有評論完畢
            break
        customers = driver.find_elements(By.CLASS_NAME, "jJc9Ad ")  # 取得評論者之區塊
        for customer in customers[pre_count:]:  # 就新獲得之評論分別蒐集評論相關資訊
            time_num, time_unit = split_time_to_num_and_unit(
                customer
            )  # 取得評論時間值與時間單位
            info_list = comment_info(
                info_list, driver, customer, time_num, time_unit
            )  # 彙整所有評論所需資訊為list
        pre_count = check_load_new_data(
            driver, "jftiEf fontBodyMedium"
        )  # 目前所獲得之評論數
        print(
            f"在{name}爬取到{pre_count}則評論，進度{round(pre_count / comments_count * 100)}%"
        )
        save_large_volumn_record(
            pre_count, dir, name
        )  # 若目前獲得之評論數超過一千筆時存檔紀錄時間以觀察其變化

    df = create_dataframe(info_list, name)  # 建立dataframe保存該店家之評論
    save_df_and_record(df, dir, name, comments_count)  # 存檔

    driver.close()  # 結束爬蟲driver


def collect_comments_by_range(dir: str, start: int, end: int) -> None:
    """
    設定爬取之夜市名稱及開始與結束之店家index
    """
    df = pd.read_csv(f"{crawler_path}/data/{dir}/{dir}_restaurant.csv")
    count = 1
    for name, link in zip(df.iloc[start:end, 0], df.iloc[start:end, 2]):
        print(f"爬取第{start + count}家評價，尚餘{end - start - count}家待爬取")
        try:
            collect_comments(name, link, dir)  # 爬取該店家之評論
        except Exception as e:
            save_error_info(name, dir, start, count, e)  # 出現錯誤則紀錄於log.txt
        time.sleep(1)
        count += 1


def collect_comments_by_list(dir: str, list: List[int]) -> None:
    """
    爬取在list中的店家評論，用做補爬集體爬取時出現錯誤而未完整爬取評論之店家用
    """
    df = pd.read_csv(f"{crawler_path}/data/{dir}/{dir}_restaurant.csv")
    count = 1
    for i in list:
        name = df.iloc[i, 0]
        link = df.iloc[i, 2]
        print(f"爬取{name}評價，尚餘{len(list) - count}家待爬取")
        try:
            collect_comments(name, link, dir)  # 爬取該店家之評論
        except Exception as e:
            print(f"爬取{name}時發生錯誤")
            path = Path(
                f"{crawler_path}/data/{dir}/log.txt"
            )  # 出現錯誤則存相關訊息於log.txt
            if not path.exists():
                path.touch()
            with open(path, "a", encoding="utf-8-sig") as f:
                f.write(f"{datetime.now().replace(microsecond=0)} : ")
                f.write(f"爬取{name}時發生錯誤\n{e}\n")
                f.close()
        time.sleep(1)
        count += 1
