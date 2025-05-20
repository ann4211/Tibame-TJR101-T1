import pandas as pd
from sqlalchemy import create_engine
from datetime import date, timedelta

# 讀取評論檔
df = pd.read_csv("/workspaces/poetry-demo-test2/toDB/comments_Cleaned_2.csv")
# 篩選日期
today = date.today()
df['create_date'] = pd.to_datetime(df['create_date']).dt.date
# someday = date.today() - timedelta(days=1)
df_date = df[df['create_date'] == today ]
print(f"篩選出 {today} 新增評論")

# 篩選後評論
df_unique_comment = df_date.drop_duplicates(subset=['nm_name', 'st_name', 'user_id', 'content_clean'], keep='last').copy()
print("篩選出當天沒有重複的COMMENT")
# 與其他Table合併
df_nightmarket = pd.read_csv("/workspaces/poetry-demo-test2/toDB/nightmarket_list.csv")
df_store = pd.read_csv("/workspaces/poetry-demo-test2/toDB/STORE.csv")
df_unique_comment = df_unique_comment.merge(df_nightmarket[['nm_id', 'nm_name']], on=['nm_name'], how='left')
df_unique_comment = df_unique_comment.merge(df_store[['st_id', 'nm_id', 'st_name']], on=['nm_id', 'st_name'], how='left')
# 去除不在store列表裡的店家評論
df_unique_comment = df_unique_comment[df_unique_comment['st_id'].notna()].copy()
# 轉換欄位型態
df_unique_comment['time_num'] = df_unique_comment['time_num'].astype(int)
df_unique_comment['months_ago'] = df_unique_comment['months_ago'].astype(float)
df_unique_comment['rating_star'] = df_unique_comment['rating_star'].astype(int)
df_unique_comment['st_id'] = df_unique_comment['st_id'].astype(int)
# 調整順序符合MySQL
new_order = ['user_id', 'nm_id', 'st_id','rating_star', 'time_num', 'time_unit', 'months_ago', 'content_clean', 'create_date', 'update_date']
df_comment_new = df_unique_comment[new_order]
# 寫入csv
df_comment_new.to_csv('/workspaces/poetry-demo-test2/toDB/comment_list.csv', mode='a', header=False, index=False, encoding='utf-8-sig')
print(f"{today} 評論寫入csv")
# 連線MySQL
host = '35.194.188.197'
port = 3306
user = 'user'
password = 'password'
db = 'BWA'
charset = 'utf8mb4'

engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{db}')
print("MySQL連線成功")
# 寫入MySQL
df_comment_new.to_sql(name='COMMENT', con=engine, if_exists='append', index=False)
print(f"{today} 評論寫入MySQL")