import pandas as pd
import re
from pathlib import Path
from datetime import date

from utils.cleaned_utils import local_guide_or_not,comment_count,photo_count,unit_to_month,clear_special_char

from airflow.decorators import task

@task
def e_load_raw_data():
    path = "./data/Crawler/comments.csv"
    df = pd.read_csv(path)
    print(df)
    return df

@task
def t_get_user_id(df):
    df["user_id"] = df["user_id"].apply(lambda x : x.split("contrib/")[1].split("/reviews?")[0])
    print(df)
    return df

@task
def t_clean_zonecode(df):
    df["地址"] = df["地址"].apply(lambda x : re.sub(r"\d{3,6}","",x[0:6]) + x[6:])
    print(df)
    return df

@task
def t_get_cityname(df):
    df.insert(1,"nm_city","")
    df["nm_city"] = df["地址"].apply(lambda x : x[0:3])
    df["地址"] = df["地址"].apply(lambda x : x[3:])
    print(df)
    return df

@task
def t_is_localguide(df):
    df.insert(3,"is_local_guide","")
    df["is_local_guide"] = df["local_guide"].apply(local_guide_or_not)
    df["local_guide"] = df["local_guide"].str.lstrip("在地嚮導· ")
    print(df)
    return df

@task
def t_get_comment_count(df):
    df.insert(4,"review_count","")
    df["review_count"] = df["local_guide"].apply(comment_count)
    return df

@task
def t_get_photo_count(df):
    df.insert(5,"photo_count","")
    df["photo_count"] = df["local_guide"].apply(photo_count)
    df.drop("local_guide",axis=1,inplace=True)
    print(df)
    return df

@task
def t_get_time(df):
    df_utom = df["time_unit"].apply(unit_to_month)
    df["time_num"] = df["time_num"].map(int)
    df.insert(9,"month_ago","")
    df["month_ago"] = df["time_num"] * df_utom
    print(df)
    return df

@task
def t_get_star(df):
    df.insert(5,"rating_star","")
    df["rating_star"] = df["rating_stars"].apply(lambda x : re.search(r"\d",x).group())
    df.drop("rating_stars",axis=1,inplace=True)
    print(df)
    return df

@task
def t_clean_comment(df):
    df["comment"] = df["comment"].apply(clear_special_char)
    print(df)
    return df

@task
def l_save_cleaned_comment(df):
    df_store = pd.read_csv("./data/Clean/restaurants_Cleaned.csv")
    df = df_store.merge(df,how="right",left_on="st_name",right_on="st_name")
    df.drop(["st_score","st_price","st_total_com","st_tag","st_url"],axis=1,inplace=True)
    path = Path("./data/Clean/comments_Cleaned.csv")
    df_comment = pd.read_csv(path)
    df_comment = pd.concat([df,df_comment])
    df_comment.drop_duplicates(subset=["nm_name","st_name","user_name","user_id"],inplace=True)
    df_comment["update_date"] = date.today()
    df_comment["month_ago"] = df_comment["month_ago"] + (pd.to_datetime(df_comment["update_date"]) - pd.to_datetime(df_comment["create_date"])).dt.days / 30
    df_comment.to_csv(path,index=False,header=True,encoding='utf-8-sig')