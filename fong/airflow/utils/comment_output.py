import pandas as pd

def comment_to_csv(df_today_new):
    df_today_new.to_csv('./data/comment_list.csv', mode='a', header=False, index=False, encoding='utf-8-sig')
    print("完成寫入csv")

def comment_to_mysql(df_today_new, engine):
    df_today_new.to_sql(name='COMMENT', con=engine, if_exists='append', index=False)
    print("完成匯入MySQL")