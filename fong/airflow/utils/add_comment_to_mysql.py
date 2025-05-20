from datetime import date
import pandas as pd
from datetime import date, timedelta
from utils.comment_output import comment_to_csv, comment_to_mysql
from utils.conn_to_mysql import conn_to_mysql


def get_today_comments(df):
    today = date.today()
    df['create_date'] = pd.to_datetime(df['create_date']).dt.date
    df_date = df[df['create_date'] == today ]
    print(f"成功取得{today}新增之評論")
    return df_date

def get_yesterday_comment(df_yesterday):
    yesterday = date.today() - timedelta(days=1)
    df_yesterday['create_date'] = pd.to_datetime(df_yesterday['create_date']).dt.date
    df_yesterday_comment = df_yesterday[df_yesterday['create_date'] == yesterday ]
    print(f"成功取得{yesterday}新增之評論")
    return df_yesterday_comment

def find_new_comment(df_date, df_nightmarket, df_store):
    df_unique_comment = df_date.drop_duplicates(subset=['nm_name', 'st_name', 'user_id', 'rating_star', 'content_clean'], keep='last').copy()
    df_unique_comment = df_unique_comment.merge(df_nightmarket[['nm_id', 'nm_name']], on=['nm_name'], how='left')
    df_unique_comment = df_unique_comment.merge(df_store[['st_id', 'nm_id', 'st_name']], on=['nm_id', 'st_name'], how='left')
    df_unique_comment = df_unique_comment[df_unique_comment['st_id'].notna()].copy()
    df_unique_comment['time_num'] = df_unique_comment['time_num'].astype(int)
    df_unique_comment['months_ago'] = df_unique_comment['months_ago'].astype(float)
    df_unique_comment['rating_star'] = df_unique_comment['rating_star'].astype(int)
    df_unique_comment['st_id'] = df_unique_comment['st_id'].astype(int)
    new_order = ['user_id', 'nm_id', 'st_id','rating_star', 'time_num', 'time_unit', 'months_ago', 'content_clean', 'create_date', 'update_date']
    df_comment_new = df_unique_comment[new_order]
    
    return df_comment_new

def drop_dup_comment(df_comment_new, df_yesterday_comment):
    df_merge = df_comment_new.merge(df_yesterday_comment, 
                        on=["nm_id", "st_id", "user_id", "rating_star"], 
                        how='left', 
                        indicator=True,
                        suffixes=('', '_y'))
    df_today_new = df_merge[df_merge['_merge'] == 'left_only'][df_comment_new.columns]
    
    return df_today_new



def add_comment_to_mysql(df, df_yesterday, df_nightmarket, df_store):
    df_date = get_today_comments(df)
    df_comment_new = find_new_comment(df_date, df_nightmarket, df_store)
    df_yesterday_comment = get_yesterday_comment(df_yesterday)
    df_today_new = drop_dup_comment(df_comment_new, df_yesterday_comment)
    if not df_today_new.empty:
        engine = conn_to_mysql()
        comment_to_csv(df_today_new)
        comment_to_mysql(df_today_new, engine)