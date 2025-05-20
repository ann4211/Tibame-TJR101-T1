from datetime import date
import pandas as pd
from utils.conn_to_mysql import conn_to_mysql
from utils.user_output import user_to_csv, user_to_mysql, update_to_csv

def get_today_comments(df):
    today = date.today()
    df['create_date'] = pd.to_datetime(df['create_date']).dt.date
    df_date = df[df['create_date'] == today ]
    print(f"成功取得{today}新增之評論")
    return df_date

def find_new_user(df_date):
    df_unique_user = df_date.drop_duplicates(subset=['user_id'], keep='last').copy()
    df_unique_user['review_count'] = df_unique_user['review_count'].fillna(0).astype(int)
    df_unique_user['photo_count'] = df_unique_user['photo_count'].fillna(0).astype(int)
    new_order = ['user_name','user_id','is_local_guide','review_count','photo_count','create_date','update_date']
    df_unique_user = df_unique_user[new_order]
    return df_unique_user

def drop_duplicate_user(df_unique_user, df_old):
    df_new = df_unique_user[~df_unique_user['user_id'].isin(df_old['user_id'])]
    return df_new

def update_user_list(df_unique_user, df_old):
    df_update = df_unique_user[df_unique_user['user_id'].isin(df_old['user_id'])]
    return df_update

def add_user_to_mysql(df, df_old):
    df_date = get_today_comments(df)
    df_unique_user = find_new_user(df_date)
    df_new = drop_duplicate_user(df_unique_user, df_old)
    df_update = update_user_list(df_unique_user, df_old)
    if not df_new.empty:
        engine = conn_to_mysql()
        update_to_csv(df_update)
        user_to_csv(df_new)
        user_to_mysql(df_new, engine)
