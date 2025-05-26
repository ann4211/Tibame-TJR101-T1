from bs4 import BeautifulSoup
from selenium.webdriver import Chrome


def check_load_count(driver: Chrome, class_: str) -> int:
    """
    目前所在動態頁面之評論資料筆數
    """
    req = driver.page_source
    soup = BeautifulSoup(req, "html.parser")
    return len(soup.find_all("div", class_=class_))
