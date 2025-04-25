import pandas as pd
import numpy as np
import re

df = pd.read_csv("fong\瑞豐店家清單.csv")
print(df)

# 清理店名
def clean_store_name(raw_name):
    parts = re.split(r'[-|()（）_\[\]。x]',raw_name)
    store_name = parts[0].strip()
    store_name = re.sub(r'[，,]', '', store_name)
    return pd.Series({
        "店名":store_name
    })

df = pd.concat([df, df['names'].apply(clean_store_name)], axis=1)
print(df)

def split_address(raw_address):
    address = re.sub(r"^\d{3,6}", '', raw_address)
    match = re.match(r"^(.{2,4}[縣市].{1,3}[鄉鎮市區])(.+)", address)
    if match:
        area = match.group(1)
        detail = match.group(2)
    else:
        area = ''
        detail = address

    return pd.Series({
        "區域": area,
        "地址": detail
        }
    )

df = pd.concat([df, df['address'].apply(split_address)], axis=1)
print(df)

df.to_csv("處理店家測試.csv")