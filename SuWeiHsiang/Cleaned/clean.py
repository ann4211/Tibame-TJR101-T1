import re
import os
import pandas as pd
from datetime import date
from typing import Tuple, Optional
from pandas import DataFrame
from dotenv import load_dotenv

load_dotenv()
data_path = os.getenv("DATA_PATH")
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
    path = f"{data_path}/{dir}/{dir}_{typename}.csv"
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


def find_city(x: str) -> Tuple[Optional[str], int]:
    """
    判斷地址所在之縣市，並回傳所在縣市名稱及縣市名稱相關字詞所在地址字串之位置
    """
    for city in municipality:  # 判斷是否在直轄市
        if city in x:
            return city, x.find(city)
    for county in counties:  # 判斷是否在省轄縣市
        if county in x:
            return county, x.find(county)
    return None, -1  # 地址漏填一級行政區


def find_second_ad_level(x: str) -> Tuple[str, int, int]:
    """
    判斷地址所在縣市之鄉鎮市區，並回傳所在縣市名稱、縣市名稱相關字詞在地址字串之位置、鄉鎮市區相關字詞在地址字串之位置
    """
    city, city_idx = find_city(x)
    if city in counties:  # 地址位在省轄縣市
        for level in second_ad_level[:3]:
            if level in x:
                return city, city_idx, x.find(level)
    elif city in municipality:  # 地址位在直轄市
        return city, city_idx, x.find("區")
    else:  # 地址漏填縣市
        for level in second_ad_level:
            if level in x:
                return city, city_idx, x.find(level)
    return city, city_idx, -1  # 地址漏填縣市及鄉鎮市區


def get_city_address(x: str) -> Tuple[str, str]:
    """
    取得去除第一二級行政區之地址
    """
    city, city_idx, second_ad_idx = find_second_ad_level(x)
    if second_ad_idx + 2 == len(x):  # 地址只填寫縣市及鄉鎮市區
        return city, re.sub(r"\d", "", x)
    if (
        city_idx < second_ad_idx
    ):  # 地址先填寫縣市在填寫鄉鎮市區(為國人慣用之地址書寫方式)
        return city, x[second_ad_idx + 1 :]
    else:  # 地址從號寫到巷弄再到街道路段再到鄉鎮市區及縣市及國家(為外國人慣用之地址書寫方式)
        if (
            "太麻里鄉" in x or "那瑪夏區" in x or "三地門鄉" in x or "阿里山鄉" in x
        ):  # 以上鄉鎮市區為台灣名稱有三個字的鄉鎮市區，其餘名稱皆為兩個字
            return city, x[: second_ad_idx - 3]
        else:
            if second_ad_idx > -1:
                return city, x[: second_ad_idx - 2]
            else:  # 漏填鄉鎮市區
                return city, x[city_idx + 3 :]


def t_clean_address(df: DataFrame) -> DataFrame:
    """
    清理地址資料，插入所在縣市之欄位，並去除地址之第一二級行政區
    """
    df.insert(1, "nm_city", "")
    df[["nm_city", "地址"]] = df["地址"].apply(get_city_address).apply(pd.Series)
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
