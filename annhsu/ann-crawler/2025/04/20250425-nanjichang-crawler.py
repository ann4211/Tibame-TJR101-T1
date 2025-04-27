"""
爬取最新
-------------------------------------------------
功能：
1. 讀取 nanjichang_clean_success.csv 的 (matched_name, matched_address)
   作為唯一店家鍵，避免重複抓取
2. 只抓「最新」排序評論；無固定上限，除非自行設定 MAX_REVIEWS
3. 以「評論數量增長」+「動態等待」邏輯持續滾動；同時偵測並點擊
   Google 插入的「顯示更多評論」按鈕，確保載入完整評論
4. 失敗店家另外記錄
-------------------------------------------------
依賴：selenium 4.11+、pandas、BeautifulSoup4
執行：python google_reviews_latest_mod.py
"""

import os
import random
import time
import logging
from pathlib import Path

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# ────────────────────────────────────────────────────────────────
# 全域常數（可依需求調整）
# ────────────────────────────────────────────────────────────────
SCROLL_IDLE_TURNS = 6            # 連續 N 次評論數未增長 → 視為到底
SCROLL_PAUSE_SEC  = (1.5, 2.5)   # 每次滾動後隨機等待區間
TIMEOUT_MIN       = 10           # 動態等待的下限秒數
TIMEOUT_MAX       = 60           # 動態等待的上限秒數
MAX_REVIEWS       = 1000      # 抓取上限；若要固定最新 N 筆可改為 N
INPUT_CSV = (
    r"C:\Users\Tibame\Downloads\ann\annhuihsu"
    r"\gm_test\nanjichang_resource\nanjichang_clean_success.csv"
)
OUTPUT_CSV        = "nanjingchang_latest_fn_reviews.csv"
FAILED_LOG        = "nanjingchang_latest_fn_reviews_failed_shops.csv"
# ────────────────────────────────────────────────────────────────

#################################################################
# Selenium 操作輔助
#################################################################

def build_driver(headless: bool = True) -> webdriver.Chrome:
    """建立並回傳 Chrome WebDriver"""
    options = Options()
    if headless:
        options.add_argument("--headless=new")  # Selenium 4.11+ 支援
    options.add_argument("--window-size=1280,1000")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--lang=zh-TW")  # 強制繁中介面，降低文字差異
    return webdriver.Chrome(options=options)


# ── 動態等待秒數計算 ─────────────────────────────────────────────

def _calc_dynamic_wait(total_reviews: int) -> int:
    """根據總評論數回傳合適的 WebDriverWait 秒數"""
    if total_reviews > 4000:
        return TIMEOUT_MAX
    if total_reviews > 3000:
        return 50
    if total_reviews > 2000:
        return 40
    if total_reviews > 1000:
        return 30
    return TIMEOUT_MIN


def _get_total_reviews(driver) -> int:
    """讀取側欄『全部 n 則評論』並回傳 n（失敗回 0）"""
    try:
        txt = driver.find_element(
            By.XPATH, "//div[@class='F7nice ']/span[2]/span/span"
        ).get_attribute("aria-label")
        return int(txt.split()[0].replace(",", ""))
    except Exception:
        return 0


# ── 滾動評論 ───────────────────────────────────────────────────
def scroll_reviews_until_loaded(driver, scrollable_div):
    idle_turns, prev_cnt = 0, 0
    wait_after_scroll = WebDriverWait(driver, 5, 0.2)  # 5 秒內等待評論增長

    while idle_turns < SCROLL_IDLE_TURNS:
        # 1️⃣ 嘗試點擊『顯示更多評論』按鈕
        more_btns = scrollable_div.find_elements(
            By.CSS_SELECTOR,
            "button[jsname='e2eb0'], button[aria-label*='更多']",
        )
        if more_btns:
            driver.execute_script("arguments[0].click()", more_btns[0])
            time.sleep(1.0)

        # 2️⃣ 直接捲到最底
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
        time.sleep(random.uniform(*SCROLL_PAUSE_SEC))

        # 3️⃣ 等待評論數真正增長（lazy‑load 完成）
        try:
            wait_after_scroll.until(
                lambda _: len(driver.find_elements(By.CLASS_NAME, "jftiEf")) > prev_cnt
            )
        except Exception:
            pass  # 5 秒內若無增長，進入 idle 評估

        curr_cnt = len(driver.find_elements(By.CLASS_NAME, "jftiEf"))
        
        # 當評論數量達到最大限制時，停止滾動
        if curr_cnt >= MAX_REVIEWS:
            break
        if curr_cnt == prev_cnt:
            idle_turns += 1
        else:
            idle_turns = 0
            prev_cnt = curr_cnt


# ── 排序為『最新』 ─────────────────────────────────────────────

def sort_reviews_by_latest(driver) -> bool:
    try:
        sort_btn = WebDriverWait(driver, TIMEOUT_MIN).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="排序評論"]'))
        )
        sort_btn.click()

        # ★ 改用容錯性更高的 XPath：同時容許 div / span + 中英文
        latest_opt = WebDriverWait(driver, TIMEOUT_MIN).until(
            EC.element_to_be_clickable((
                By.XPATH,
                (
                 '//div[@role="menuitemradio" and '
                 '(normalize-space(.//div)="最新"   or normalize-space(.//div)="Newest" '
                 ' or normalize-space(.//span)="最新" or normalize-space(.//span)="Newest")]'
                )
            ))
        )
        ActionChains(driver).move_to_element(latest_opt).click().perform()
        logging.info("✔ 已切換為『最新』排序")
        return True
    except Exception as e:
        logging.warning(f"❌ 無法切換『最新』排序：{e}")
        return False


# ── 工具 ───────────────────────────────────────────────────────

def _txt_or_blank(elem, by, cls) -> str:
    return elem.find_element(by, cls).text if elem.find_elements(by, cls) else ""


def parse_comment_elem(elem, shop_name: str, shop_addr: str) -> dict:
    try:
        # --- 既有解析邏輯 ---
        # 長評點『更多』
        if elem.find_elements(By.CLASS_NAME, "w8nwRe"):
            elem.find_element(By.CLASS_NAME, "w8nwRe").click()
            time.sleep(0.3)
        rating = (
            elem.find_element(By.CLASS_NAME, "kvMYJc").get_attribute("aria-label")
            if elem.find_elements(By.CLASS_NAME, "kvMYJc")
            else ""
        )
        return {
            "matched_name": shop_name,
            "matched_address": shop_addr,
            "author": _txt_or_blank(elem, By.CLASS_NAME, "d4r55"),
            "role":   _txt_or_blank(elem, By.CLASS_NAME, "RfnDt"),
            "rating": rating,
            "time":   _txt_or_blank(elem, By.CLASS_NAME, "rsqaWe"),
            "content":_txt_or_blank(elem, By.CLASS_NAME, "wiI7pd"),
        }
    except Exception as e:
        logging.warning(f"⚠ 解析 {shop_name} 單筆評論失敗：{e}")
        return {
            "matched_name": shop_name,
            "matched_address": shop_addr,
            "author": "",
            "role": "",
            "rating": "",
            "time": "",
            "content": "",
        }


#################################################################
# 爬一間店家：搜尋 → 評論 → 最新排序 → 滾到底 → 解析
#################################################################
def get_reviews_from_shop(shop_name: str, shop_addr: str, driver, max_retries=3) -> pd.DataFrame:
    logging.info(f"🔍 開始處理：{shop_name}")

    retries = 0
    while retries < max_retries:
        try:
            # 1. 進入 Google Maps、搜尋店名
            driver.get("https://www.google.com/maps")
            WebDriverWait(driver, TIMEOUT_MIN).until(
                EC.presence_of_element_located((By.ID, "searchboxinput"))
            )
            sb = driver.find_element(By.ID, "searchboxinput")
            sb.clear()
            sb.send_keys(shop_name, Keys.RETURN)

            # 2. 讀取總評論數並設定動態等待
            total_reviews = _get_total_reviews(driver)
            logging.info(f"📝 Google 顯示評論總數：{total_reviews}")

            # 設定最大評論數上限
            total_reviews = min(total_reviews, MAX_REVIEWS)

            # 計算動態等待時間
            wait_sec = _calc_dynamic_wait(total_reviews)

            # 3. 進入評論分頁
            review_tab = WebDriverWait(driver, wait_sec).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label,'評論')]"))
            )
            review_tab.click()

            # 4. 切換到「最新」排序
            if not sort_reviews_by_latest(driver):
                raise RuntimeError("切換最新排序失敗")

            # 5. 等待評論容器出現，並開始滾動載入
            scrollable_div = WebDriverWait(driver, wait_sec).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(@class,'m6QErb') and contains(@class,'DxyBCb')]")
                )
            )
            scroll_reviews_until_loaded(driver, scrollable_div)

            # 6. 解析所有評論元素
            comments_elems = driver.find_elements(By.CLASS_NAME, "jftiEf")
            logging.info(f"📋 抓取到 {len(comments_elems)} 筆評論")

            rows = []
            for idx, elem in enumerate(comments_elems, start=1):
                rows.append(parse_comment_elem(elem, shop_name, shop_addr))
                if idx % 3 == 0:
                    logging.info(f"⏱ 已解析 {idx} 筆評論...")

            # 如果抓取到評論則返回 DataFrame
            if rows:
                return pd.DataFrame(rows)

            # 如果無評論，記錄並返回空 DataFrame
            logging.warning(f"⚠ {shop_name} 無評論")
            return pd.DataFrame()

        except Exception as e:
            retries += 1
            logging.error(f"❌ 爬取 {shop_name} 失敗，錯誤：{e}，重試 {retries}/{max_retries}")
            
            # 如果重試次數達到最大限制，則返回空的 DataFrame
            if retries >= max_retries:
                logging.warning(f"⚠ {shop_name} 最終未能成功爬取")
                return pd.DataFrame()

            # 等待一段時間再重試
            time.sleep(random.uniform(3, 5))  # 3到5秒的隨機等待時間



#################################################################
# 一次爬五家
#################################################################
def batch_process_shops(
    shops: list[tuple[str, str]],
    driver,
    batch_size: int = 2,
    order =['鈺師傅上海生煎包']
) -> tuple[list[pd.DataFrame], list[dict]]:
    """
    shops:      [(shop_name, shop_addr), ...]
    driver:     Selenium WebDriver
    batch_size: 每批處理店家數量
    order:      若提供，依此店名順序優先處理，其餘店家接在後面
    """
    # 1. 如有指定 order，先排序
    if order:
        shop_map = {name: (name, addr) for name, addr in shops}
        ordered = []
        for name in order:
            if name in shop_map:
                ordered.append(shop_map.pop(name))
        ordered.extend(shop_map.values())
        shops = ordered

    all_reviews = []
    failed_shops = []
    total_shops = len(shops)

    # 2. 分批處理
    for i in range(0, total_shops, batch_size):
        batch = shops[i : i + batch_size]
        logging.info(f"開始處理批次 {i // batch_size + 1}，共 {len(batch)} 家店")

        for shop_name, shop_addr in batch:
            logging.info(f"➡ 處理店家：{shop_name}")
            try:
                reviews = get_reviews_from_shop(shop_name, shop_addr, driver)
                if reviews.empty:
                    failed_shops.append({
                        "matched_name": shop_name,
                        "matched_address": shop_addr
                    })
                else:
                    all_reviews.append(reviews)
            except Exception as e:
                logging.error(f"❌ 處理 {shop_name} 時出現錯誤：{e}")
                failed_shops.append({
                    "matched_name": shop_name,
                    "matched_address": shop_addr
                })

        # 批次間隨機小憩，避免被封
        time.sleep(random.uniform(5, 10))

    return all_reviews, failed_shops

#################################################################
# 主程式
#################################################################

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )

    driver = build_driver(headless=True)

    # 讀 CSV，補空值並組成唯一店家列表
    df_input = pd.read_csv(INPUT_CSV, dtype=str).fillna("")
    shops = (
        df_input[["matched_name", "matched_address"]]
        .drop_duplicates()
        .to_records(index=False)
        .tolist()
    )

    all_reviews, failed_shops = batch_process_shops(shops, driver)

    # 成功結果輸出
    if all_reviews:
        Path(OUTPUT_CSV).parent.mkdir(parents=True, exist_ok=True)
        pd.concat(all_reviews, ignore_index=True).to_csv(
            OUTPUT_CSV, index=False, encoding="utf-8-sig"
        )
        logging.info(f"🎉 全部完成，輸出 {OUTPUT_CSV}")

    # 失敗名單輸出
    if failed_shops:
        pd.DataFrame(failed_shops).to_csv(
            FAILED_LOG,
            mode="a",
            header=not os.path.exists(FAILED_LOG),
            index=False,
            encoding="utf-8-sig",
        )
        logging.info(f"⚠ 有 {len(failed_shops)} 間店爬失敗，名單寫入 {FAILED_LOG}")

    driver.quit()


if __name__ == "__main__":
    main()
