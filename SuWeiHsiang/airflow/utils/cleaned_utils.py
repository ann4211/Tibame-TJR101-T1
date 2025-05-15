import pandas as pd
import re

def local_guide_or_not(x):
    if pd.isna(x) or "在地嚮導" not in x:
        return "FALSE"
    else :
        return "TRUE"

def comment_count(x):
    if pd.isna(x):
        return 0
    x = x.rstrip("則評論")
    match = re.search(r"\d*",x).group()
    return int(match) if match else 0

def photo_count(x):
    if pd.isna(x):
        return 0
    x = x.split("則評論 · ")[-1]
    match = re.search(r"\d*",x).group()
    return int(match) if match else 0

def t_get_month_ago(df):
    if   df["time_unit"] == "天"   : return int(df["time_num"]) / 30
    elif df["time_unit"] == "週"   : return int(df["time_num"]) / 4
    elif df["time_unit"] == "個月" : return int(df["time_num"]) + 0.5
    elif df["time_unit"] == "年"   : return int(df["time_num"]) * 12 + 6
    else                           : return 0

def clear_special_char(x):
    if pd.isna(x):
        return
    else:
        return re.sub(r"[\n\r]"," ",x)