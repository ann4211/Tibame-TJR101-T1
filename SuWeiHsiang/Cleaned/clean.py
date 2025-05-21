import re
import os
import pandas as pd
from datetime import date
from typing import Tuple, Optional
from pandas import DataFrame
from dotenv import load_dotenv

load_dotenv()
crawler_path = os.getenv("CRAWLER_PATH")
clean_path = os.getenv("CLEANED_PATH")


second_ad_level = ["市", "鄉", "鎮", "區"]
municipality = ["台北市", "新北市", "桃園市", "台中市", "高雄市", "台南市"]
counties = [
    "基隆市",
    "新竹市",
    "新竹縣",
    "苗栗縣",
    "南投市",
    "彰化縣",
    "雲林縣",
    "嘉義縣",
    "屏東縣",
    "台東縣",
    "花蓮縣",
    "宜蘭縣",
    "澎湖縣",
    "金門縣",
    "連江縣",
]


def e_load_raw_data(dir: str, typename: str) -> DataFrame:
    """
    取出資料
    """
    path = f"{crawler_path}/data/{dir}/{dir}_{typename}.csv"
    df = pd.read_csv(path)
    return df


def t_clean_tag(df: DataFrame) -> DataFrame:
    """
    清除tag中的中括號及上引號
    """

    def clean_tag(x: str) -> str:
        """
        清除中括號及上引號
        """
        return re.sub(r"[\[\'\]]*", "", x)

    df["st_tag"] = df["st_tag"].apply(clean_tag)
    return df


def t_get_user_id(df: DataFrame) -> DataFrame:
    """
    取得評論者ID
    """
    df["user_id"] = df["user_id"].apply(
        lambda x: x.split("contrib/")[1].split("/reviews?")[0]
    )
    return df


def find_city(x: str) -> Tuple[str, int]:
    """
    判斷地址所在之縣市，並回傳所在縣市名稱及縣市名稱相關字詞所在地址字串之位置
    """
    for city in municipality:  # 判斷是否在直轄市
        if city in x:
            city_re = re.search(city, x)
            city_end = city_re.span()[1]
            city = city_re.group()
            return city, city_end
    for city in counties:  # 判斷是否在省轄縣市
        if city in x:
            city_re = re.search(city, x)
            city_end = city_re.span()[1]
            city = city_re.group()
            return city, city_end
    return "", 0  # 地址漏填一級行政區


def find_dist(x: str, city: str, city_end: int) -> Tuple[str, int]:
    """
    判斷地址所在縣市之鄉鎮市區，並回傳鄉鎮市區名稱、鄉鎮市區相關字詞在地址字串之位置
    """
    if city in municipality:  # 地址在直轄市
        dist_re = re.match(r"(.*?)區", x[city_end:])
        if dist_re is not None:
            dist_end = city_end + dist_re.span()[1]
            dist = dist_re.group()
        else:
            dist_end = city_end
            dist = ""
    elif city in counties:  # 地址在省轄縣市
        dist_re = re.match(r"(.*?)[鄉鎮市]", x[city_end:])
        if dist_re is not None:
            dist_end = city_end + dist_re.span()[1]
            dist = dist_re.group()
        else:
            dist_end = city_end
            dist = ""
    else:  # 不知道地址位在哪個縣市
        dist_re = re.match(r"(.*?)[鄉鎮市區]", x[city_end:])
        if dist_re is not None:
            dist_end = city_end + dist_re.span()[1]
            dist = dist_re.group()
        else:
            dist_end = city_end
            dist = ""
    return dist, dist_end


def taiwan_address(
    x: str, city: str, dist: str, dist_end: int
) -> Tuple[str, str, bool]:
    """
    地址書寫方式為國人慣用之書寫方式
    """
    road_re = re.match(r"(.*?)[路街]", x[dist_end:])
    if road_re is not None:
        road_end = dist_end + road_re.span()[1]
        road = road_re.group()
    else:
        road_end = dist_end
        road = ""

    sec_re = re.match(r"(.*?)段", x[road_end:])
    if sec_re is not None:
        sec_end = road_end + sec_re.span()[1]
        sec = sec_re.group()
    else:
        sec_end = road_end
        sec = ""

    lane_re = re.match(r"(.*?)巷", x[sec_end:])
    if lane_re is not None:
        lane_end = sec_end + lane_re.span()[1]
        lane = lane_re.group()
    else:
        lane_end = sec_end
        lane = ""

    alley_re = re.match(r"(.*?)弄", x[lane_end:])
    if alley_re is not None:
        alley_end = lane_end + alley_re.span()[1]
        alley = alley_re.group()
    else:
        alley_end = lane_end
        alley = ""

    no_re = re.match(r"(.*?)號", x[alley_end:])
    if no_re is not None:
        no_end = alley_end + no_re.span()[1]
        no = no_re.group()
    else:
        no_end = alley_end
        no = ""

    no2_re = re.match(r"(.*?)號", x[no_end:])
    if no2_re is not None:
        no2_end = no_end + no2_re.span()[1]
        no2 = no2_re.group()
    else:
        no2_end = no_end
        no2 = ""

    is_taiwan_address = True  # 確認是否真為台灣慣用地址格式
    if (
        dist == "" and re.sub(r"\d+", "", x[no2_end]) == ""
    ):  # 如果沒有獲得二級行政區且未有任何備註性質之文字，則視為非台灣慣用之地址格式
        is_taiwan_address = False
        address = ""
        return city, address, is_taiwan_address

    address = dist + road + sec + lane + alley + no + no2 + x[no2_end:]
    return city, address, is_taiwan_address


def west_address(x: str, city: str, city_end: int) -> Tuple[str, str]:
    """
    地址書寫方式為西方人慣用之書寫方式
    """
    no_re = re.match(r"(.*?)號", x)
    if no_re is not None:
        no_end = no_re.span()[1]
        no = no_re.group()
    else:
        no_end = 0
        no = ""

    no2_re = re.match(r"(.*?)號", x[no_end:])
    if no2_re is not None:
        no2_end = no_end + no_re.span()[1]
        no2 = no2_re.group()
    else:
        no2_end = no_end
        no2 = ""

    alley_re = re.match(r"(.*?)弄", x[no2_end:])
    if alley_re is not None:
        alley_end = no2_end + alley_re.span()[1]
        alley = alley_re.group()
    else:
        alley_end = no2_end
        alley = ""

    lane_re = re.match(r"(.*?)巷", x[alley_end:])
    if lane_re is not None:
        lane_end = alley_end + lane_re.span()[1]
        lane = lane_re.group()
    else:
        lane_end = alley_end
        lane = ""

    sec_re = re.match(r"(.*?)段", x[lane_end:])
    if sec_re is not None:
        sec_end = lane_end + sec_re.span()[1]
        sec = sec_re.group()
    else:
        sec_end = lane_end
        sec = ""

    road_re = re.match(r"(.*?)[路街]", x[sec_end:])
    if road_re is not None:
        road_end = sec_end + road_re.span()[1]
        road = road_re.group()
    else:
        road_end = sec_end
        road = ""

    if city in municipality:
        dist_re = re.match(r"(.*?)區", x[road_end:city_end])
        if dist_re is not None:
            dist = dist_re.group()
        else:
            dist = ""
    elif city in counties:
        dist_re = re.match(r"(.*?)[鄉鎮市]", x[road_end:city_end])
        if dist_re is not None:
            dist = dist_re.group()
        else:
            dist = ""
    else:
        dist_re = re.match(r"(.*?)[鄉鎮市區]", x[road_end:city_end])
        if dist_re is not None:
            dist = dist_re.group()
        else:
            dist = ""

    address = dist + road + sec + lane + alley + no + no2
    return city, address


def get_address(x: str) -> Tuple[str, str]:
    """
    依照地址書寫方式型態轉換為國人慣用之書寫型態
    """
    city, city_end = find_city(x)
    dist, dist_end = find_dist(x, city, city_end)

    if city_end <= dist_end:  # 國人慣用之地址書寫方式為先寫一級行政區再寫二級行政區
        city, address, is_taiwan_address = taiwan_address(x, city, dist, dist_end)
        if is_taiwan_address:
            return city, address
        else:
            return west_address(x, city, city_end)
    else:  # 西方人慣用之地址書寫方式為先寫二級行政區再寫一級行政區
        return west_address(x, city, city_end)


def t_clean_address(df: DataFrame) -> DataFrame:
    """
    清理地址資料，插入所在縣市之欄位
    """
    df.insert(1, "nm_city", "")
    df[["nm_city", "st_address"]] = df["st_address"].apply(get_address).apply(pd.Series)
    return df


def t_is_localguide(df: DataFrame) -> DataFrame:
    """
    標記是否為在地嚮導
    """

    def local_guide_or_not(x: str) -> str:
        """
        判斷是否為在地嚮導
        """
        if pd.isna(x) or "在地嚮導" not in x:
            return "FALSE"
        else:
            return "TRUE"

    df.insert(3, "is_local_guide", "")
    df["is_local_guide"] = df["local_guide"].apply(local_guide_or_not)
    df["local_guide"] = df["local_guide"].str.lstrip("在地嚮導· ")
    return df


def t_get_comment_count(df: DataFrame) -> DataFrame:
    """
    獲得評論者之發布評論數
    """

    def comment_count(x: str) -> int:
        """
        獲得單一評論者之發布評論數
        """
        if pd.isna(x):
            return 0
        x = x.rstrip("則評論")
        return re.search(r"\d*", x).group()

    df.insert(4, "review_count", "")
    df["review_count"] = df["local_guide"].apply(comment_count)
    return df


def t_get_photo_count(df: DataFrame) -> DataFrame:
    """
    獲得評論者之發布照片數
    """

    def photo_count(x: str) -> int:
        """
        獲得單一評論者之發布照片數
        """
        if pd.isna(x):
            return 0
        x = x.split("則評論 · ")[-1]
        return re.search(r"\d*", x).group()

    df.insert(5, "photo_count", "")
    df["photo_count"] = df["local_guide"].apply(photo_count)
    df.drop("local_guide", axis=1, inplace=True)
    return df


def t_get_time(df: DataFrame) -> DataFrame:
    """
    換算評論時間為以月為單位之月數
    """

    def unit_to_month(df: DataFrame) -> float:
        """
        評論時間在一天內計為0個月，一天計為1/30個月，一週計為1/4個月，一個月計為1.5個月(兩個月計為2.5個月以此類推)，一年計為18個月(兩年計為30個月以此類推)
        """
        if df["time_unit"] == "天":
            return int(df["time_num"]) / 30
        elif df["time_unit"] == "週":
            return int(df["time_num"]) / 4
        elif df["time_unit"] == "個月":
            return int(df["time_num"]) + 0.5
        elif df["time_unit"] == "年":
            return int(df["time_num"]) * 12 + 6
        else:
            return 0

    df.insert(9, "months_ago", "")
    df["months_ago"] = df.apply(unit_to_month, axis=1)
    return df


def t_get_star(df: DataFrame) -> DataFrame:
    """
    獲得評論之星等數
    """
    df.insert(6, "rating_star", "")
    df["rating_star"] = df["rating_stars"].apply(lambda x: re.search(r"\d", x).group())
    df.drop("rating_stars", axis=1, inplace=True)
    return df


def t_clean_comment(df: DataFrame) -> DataFrame:
    """
    進行評論內容之清理
    """

    def clear_special_char(x: str) -> Optional[str]:
        """
        清除換行符號及空格符號
        """
        if pd.isna(x):
            return
        else:
            return re.sub(r"[\n\r\t]", " ", x)

    df["comment"] = df["comment"].apply(clear_special_char)
    df.rename(columns={"comment": "content_clean"}, inplace=True)
    return df


def t_adjust_columns(
    df_store: DataFrame, df_comment: DataFrame, nm_name_ch: str
) -> Tuple[DataFrame, DataFrame]:
    """
    調整店家表及評論表之欄位
    """
    df_store.drop(["latitude", "longitude", "distance"], axis=1, inplace=True)
    df_store.insert(0, "nm_name", nm_name_ch)
    df_store.rename(
        columns={"餐廳名稱": "st_name", "地址": "st_address", "餐廳連結": "st_url"},
        inplace=True,
    )
    df = df_store.merge(df_comment, how="right", left_on="st_name", right_on="st_name")
    df.drop(
        ["st_score", "st_price", "st_total_com", "st_tag", "st_url"],
        axis=1,
        inplace=True,
    )
    return df_store, df


def t_update_months_ago(df_comment: DataFrame) -> Tuple[DataFrame, DataFrame]:
    """
    更新Update_date及months_ago
    """
    df_comment["months_ago"] = (
        df_comment["months_ago"]
        + (
            pd.to_datetime(date.today()) - pd.to_datetime(df_comment["create_date"])
        ).dt.days
        / 30
    )
    df_comment["update_date"] = date.today()
    return df_comment


def l_save_data_to_csv(
    df_store: DataFrame, df_comment: DataFrame, nm_name: str
) -> None:
    """
    儲存店家表及評論表
    """
    df_store.to_csv(
        f"{clean_path}/{nm_name}_restaurants_Cleaned.csv",
        index=False,
        header=True,
        encoding="utf-8-sig",
    )
    df_comment.to_csv(
        f"{clean_path}/{nm_name}_comment_Cleaned.csv",
        index=False,
        header=True,
        encoding="utf-8'sig",
    )
