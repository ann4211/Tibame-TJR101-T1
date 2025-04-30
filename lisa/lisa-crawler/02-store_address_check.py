from selenium.webdriver import Chrome
import pandas as pd
import time

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

def store_address_check(night_market , address_keys):
    print(f"正在處理：{night_market}")
    df = pd.read_csv(f"./data/output/store_list/{night_market}.csv")

    store_information = []
    review_store = set()

    for index, row in df.iterrows():
        store = row["餐廳名稱"]
        link = row["餐廳連結"]

        store_address_1 = ""
        store_address_2 = ""

        try:
            driver = Chrome()
            driver.get(link)
            time.sleep(3)

            # 用準確地址來做比對
            try:
                store_address_1 = driver.find_element(By.CLASS_NAME, "CsEnBe").get_attribute("aria-label")
                store_address_1 = store_address_1.replace("地址：", "").replace("地址:", "").strip()

                if any(keyword in store_address_1 for keyword in address_keys):
                    print(f"{store} 是 {night_market} 店家")
                    if (store , store_address_1) not in review_store:
                        review_store.add((store , store_address_1))
                        store_information.append({
                            "夜市名稱": address_keys[2],
                            "餐廳名稱": store,
                            "餐廳地址": store_address_1,
                            "餐廳連結": link
                        })
                        continue
                    else:
                        print(f"{store}重複，不存取資料")
                        continue
                        
            except Exception as e:
                print(f"抓取{store}地址失敗原因：\n{e}")

            finally:
                time.sleep(2)

            # 用所在位置來比對
            try:
                store_address_2 = driver.find_element(By.XPATH, '//div[contains(text(),"所在地點")]').text
                if any(keyword in store_address_2 for keyword in address_keys):
                    print(f"{store} 是 {night_market} 店家")
                    if (store , store_address_1) not in review_store:
                        review_store.add((store , store_address_1))
                        store_information.append({
                            "夜市名稱": address_keys[2],
                            "餐廳名稱": store,
                            "餐廳地址": store_address_1,
                            "餐廳連結": link
                        })
                else:
                    print(f"{store} 不是 {night_market} 店家")
            
            except NoSuchElementException:
                print(f"{store}不是{night_market}所在地")
            
            except Exception as e:
                print(f"抓取{store}失敗原因：\n{e}")

            finally:
                time.sleep(2)

        except Exception as e:
            print(f"抓取{store}有問題：\n{e}")
        
        finally:
            driver.quit()

    # 寫入資料
    df = pd.DataFrame(store_information)
    df.to_csv(f"./data/output/store_list_address/{night_market}_check.csv", index=False, header=True, encoding='utf-8-sig')
    print(f"已儲存 {len(store_information)} 筆資料至 {night_market}_check.csv")


if __name__ == "__main__" :
    nightmarket_address = {
        "Dadong Night Market": ["台南市東區", "林森路一段", "大東夜市"],
        "Tainan Flower Night Market": ["台南市北區", "海安路", "花園夜市"],
        "Wusheng Night Market": ["台南市中西區", "武聖路", "武聖夜市"]
        }

    for night_market, address_keys in nightmarket_address.items():
        store_address_check(night_market, address_keys)