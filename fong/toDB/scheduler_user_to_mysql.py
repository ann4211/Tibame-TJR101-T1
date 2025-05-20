import pandas as pd
from sqlalchemy import create_engine
from datetime import date

# 讀取評論檔
df = pd.read_csv("/workspaces/poetry-demo-test2/toDB/comments_Cleaned_2.csv")
# 篩選日期
today = date.today()
df['create_date'] = pd.to_datetime(df['create_date']).dt.date
df_date = df[df['create_date'] == today ]
print(f"篩選出{today}新增評論")

# 篩選後評論
df_unique_user = df_date.drop_duplicates(subset=['user_id'], keep='last').copy()
print("篩選出當天沒有重複的USER")
# 轉換欄位型態
df_unique_user['review_count'] = df_unique_user['review_count'].fillna(0).astype(int)
df_unique_user['photo_count'] = df_unique_user['photo_count'].fillna(0).astype(int)
# 調整順序符合MySQL
new_order = ['user_name','user_id','is_local_guide','review_count','photo_count','create_date','update_date']
df_unique_user = df_unique_user[new_order]
print("準備好格式存檔及匯入MySQL")
# 讀取舊有的user_list
df_old = pd.read_csv("/workspaces/poetry-demo-test2/toDB/user_list.csv")
# 排除已出現過的留言者名稱
df_new = df_unique_user[~df_unique_user['user_id'].isin(df_old['user_id'])]
print("排除已存在的USER")

# 建立SQL連線
host = '35.194.188.197'
port = 3306
user = 'user'
password = 'password'
db = 'BWA'
charset = 'utf8mb4'

engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{db}')
print("MySQL連線成功!")

# 寫入CSV
df_new.to_csv('/workspaces/poetry-demo-test2/toDB/user_list.csv', mode='a', header=False, index=False, encoding='utf-8-sig')
# 寫入SQL
df_new.to_sql(name='USER' , con=engine, if_exists='append', index=False)