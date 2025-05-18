import pandas as pd
from pandas import DataFrame
from typing import Optional
import re


def local_guide_or_not(x: str) -> bool:
    """
    判斷是否為在地嚮導
    """
    if pd.isna(x) or "在地嚮導" not in x:
        return False
    else:
        return True


def comment_count(x: str) -> int:
    """
    獲得單一評論者之發布評論數
    """
    if pd.isna(x):
        return 0
    x = x.rstrip("則評論")
    match = re.search(r"\d*", x).group()
    return int(match) if match else 0


def photo_count(x: str) -> int:
    """
    獲得單一評論者之發布照片數
    """
    if pd.isna(x):
        return 0
    x = x.split("則評論 · ")[-1]
    match = re.search(r"\d*", x).group()
    return int(match) if match else 0


def t_get_month_ago(df: DataFrame) -> float:
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


def clear_special_char(x: str) -> Optional[str]:
    """
    清除換行符號及空格符號
    """
    if pd.isna(x):
        return
    else:
        return re.sub(r"[\n\r\t]", " ", x)
