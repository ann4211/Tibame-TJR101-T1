import os
from dotenv import load_dotenv
from collect_restaurants import (
    collect_links,
    get_abs_locate,
    with_dist,
    drop_faraway,
    faraway_restaurants,
    get_restaurant_info,
)
from collect_comments import collect_comments_by_range, collect_comments_by_list

load_dotenv()
crawler_path = os.getenv("CRAWLER_PATH")  # 爬蟲相關檔案所在資料夾

if __name__ == "__main__":
    nm_name_ch = "寧夏夜市"  # 店家的中文名稱(作為Google地圖搜尋關鍵字)
    typename = "小吃"  # 店家的類型(如小吃、餐廳等等)
    nm_name = "NingXia"  # 店家的英文名稱(為了創建檔案存取資料夾用)
    target_latitude = 25.055534  # 店家的緯度
    target_longitude = 121.515107  # 店家的經度
    distance = 0.4  # 店家與夜市的距離(方圓幾公里內的店家才可以算是在夜市裡)
    collect_links(nm_name_ch, typename, nm_name)
    get_abs_locate(
        f"{crawler_path}/data/{nm_name}//restaurants.csv", nm_name_ch, nm_name
    )
    with_dist(
        f"{crawler_path}/data/{nm_name}/with_abs_locate.csv",
        target_latitude,
        target_longitude,
        nm_name,
    )
    drop_faraway(
        f"{crawler_path}/data/{nm_name}/with_dist.csv",
        nm_name,
        distance,
    )
    faraway_restaurants(
        f"{crawler_path}/data/{nm_name}/with_dist.csv", nm_name, distance
    )
    get_restaurant_info(
        f"{crawler_path}/data/{nm_name}/restaurant_around_corner.csv", nm_name
    )
    # 爬取餐廳評論爬取餐廳評論之參數請設定
    start = 0  # 要從第幾家開始蒐集評論(目前到樂華夜市第100家)
    end = 1  # 要從蒐集評論到第幾家
    collect_comments_by_range(nm_name, start, end)

    # 需要補爬評論之餐廳名單
    # re_crawl = [6]
    # collect_comments_by_list(nm_name, re_crawl)
