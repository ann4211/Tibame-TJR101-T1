import pandas as pd
import numpy as np
import re


df = pd.read_csv("fong\一中商圈攤位評論.csv")
# 填空值
df = df.fillna("null")

# 清理評等
df['評分'] = df["評分"].str.extract('(\d+)').astype(int)
print(df['留言者身分'])
print(df)

# 清理身分欄位
def prase_user_info(text):
    identify = None
    reviews = 0
    photos = 0
    
    if '在地嚮導' in text:
        identify = '在地嚮導'

    reviews_match = re.search(r"([\d,]+)\s*則評論", text)
    if reviews_match:
        reviews = int(reviews_match.group(1).replace(",",""))
    else:
        reviews == 0

    photos_match = re.search(r"([\d,]+)\s*張相片", text)
    if photos_match:
        photos = int(photos_match.group(1).replace(",",""))
    else:
        photos == 0
    
    return pd.Series({
        "身分": identify,
        "評論數": reviews,
        "相片數": photos
    })

df_new = pd.concat([df, df['留言者身分'].apply(prase_user_info)], axis=1)
df_new['評論數'] = df_new['評論數'].astype('Int64')
df_new['相片數'] = df_new['相片數'].astype('Int64')
print(df_new)


df_new.to_csv("處理測試後.csv", index=False)

