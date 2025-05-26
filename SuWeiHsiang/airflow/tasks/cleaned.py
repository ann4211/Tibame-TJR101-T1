import pandas as pd
from pandas import DataFrame
import re
from pathlib import Path
from datetime import date

from utils.cleaned_utils import (
    local_guide_or_not,
    comment_count,
    photo_count,
    t_get_month_ago,
    clear_special_char,
)

from airflow.decorators import task


@task
def e_load_raw_data() -> DataFrame:
    """
    取出資料
    """
    path = "./data/Crawler/comments.csv"
    df = pd.read_csv(path, encoding="utf-8-sig")
    print(df)
    return df


@task
def t_get_user_id(df: DataFrame) -> DataFrame:
    """
    取得評論者ID
    """
    df["user_id"] = df["user_id"].apply(
        lambda x: x.split("contrib/")[1].split("/reviews?")[0]
    )
    print(df)
    return df


@task
def t_is_localguide(df: DataFrame) -> DataFrame:
    """
    標記是否為在地嚮導
    """
    df.insert(3, "is_local_guide", "")
    df["is_local_guide"] = df["local_guide"].apply(local_guide_or_not)
    df["local_guide"] = df["local_guide"].str.lstrip("在地嚮導· ")
    return df


@task
def t_get_comment_count(df: DataFrame) -> DataFrame:
    """
    獲得評論者之發布評論數
    """
    df.insert(4, "review_count", "")
    df["review_count"] = df["local_guide"].apply(comment_count)
    return df


@task
def t_get_photo_count(df: DataFrame) -> DataFrame:
    """
    獲得評論者之發布照片數
    """
    df.insert(5, "photo_count", "")
    df["photo_count"] = df["local_guide"].apply(photo_count)
    df.drop("local_guide", axis=1, inplace=True)
    return df


@task
def t_get_time(df: DataFrame) -> DataFrame:
    """
    換算評論時間為以月為單位之月數
    """
    df.insert(9, "months_ago", "")
    df["months_ago"] = df.apply(t_get_month_ago, axis=1)
    return df


@task
def t_get_star(df: DataFrame) -> DataFrame:
    """
    獲得評論之星等數
    """
    df.insert(6, "rating_star", "")
    df["rating_star"] = df["rating_stars"].apply(lambda x: re.search(r"\d", x).group())
    df.drop("rating_stars", axis=1, inplace=True)
    return df


@task
def t_clean_comment(df: DataFrame) -> DataFrame:
    """
    進行評論內容之清理
    """
    df["comment"] = df["comment"].apply(clear_special_char)
    df.rename(columns={"comment": "content_clean"}, inplace=True)
    return df


@task
def t_adjust_columns(df: DataFrame) -> DataFrame:
    """
    調整欄位
    """
    df_store = pd.read_csv("./data/Clean/restaurants_Cleaned.csv", encoding="utf-8-sig")
    df = df_store.merge(df, how="right", left_on="st_name", right_on="st_name")
    df.drop(
        ["st_score", "st_price", "st_total_com", "st_tag", "st_url"],
        axis=1,
        inplace=True,
    )
    path = Path("./data/Clean/comments_Cleaned.csv")
    df_comment = pd.read_csv(path, encoding="utf-8-sig")
    df_comment = pd.concat([df_comment, df])
    df_comment.drop_duplicates(
        subset=["nm_name", "st_name", "user_name", "user_id"], keep="last", inplace=True
    )
    df_comment["rating_star"] = pd.to_numeric(
        df_comment["rating_star"], errors="coerce"
    )
    df_comment["review_count"] = pd.to_numeric(
        df_comment["review_count"], errors="coerce"
    )
    df_comment["photo_count"] = pd.to_numeric(
        df_comment["photo_count"], errors="coerce"
    )
    df_comment["time_num"] = pd.to_numeric(df_comment["time_num"], errors="coerce")
    df_comment["months_ago"] = pd.to_numeric(df_comment["months_ago"], errors="coerce")
    df_comment["create_date"] = pd.to_datetime(
        df_comment["create_date"], errors="coerce"
    )
    df_comment["update_date"] = pd.to_datetime(
        df_comment["update_date"], errors="coerce"
    )
    return df_comment


@task
def t_update_months_ago(df: DataFrame) -> DataFrame:
    """
    更新Update_date及months_ago
    """
    df["months_ago"] = (
        df["months_ago"]
        + (pd.to_datetime(date.today()) - pd.to_datetime(df["update_date"])).dt.days
        / 30
    )
    df["update_date"] = date.today()
    return df


@task
def l_save_cleaned_comment(df: DataFrame) -> None:
    """
    儲存清理後之新評論
    """
    path = Path("./data/Clean/comments_Cleaned.csv")
    df.to_csv(path, index=False, header=True, encoding="utf-8-sig")
