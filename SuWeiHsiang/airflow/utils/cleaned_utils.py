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

def unit_to_month(x):
    if   "天" in x : return 1 / 30
    elif "週" in x : return 0.25
    elif "月" in x : return 1.5
    elif "年" in x : return 18
    else           : return 0

def clear_special_char(x):
    if pd.isna(x):
        return
    else:
        return re.sub(r"[\n\r]"," ",x)