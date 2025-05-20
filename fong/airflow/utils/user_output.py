import pandas as pd

def user_to_csv(df_new):
    df_new.to_csv('./data/user_list.csv', mode='a', header=False, index=False, encoding='utf-8-sig')
    print("完成寫入csv")

def update_to_csv(df_update):
    df_update.to_csv('./data/update_user.csv', header=True, index=False, encoding='utf-8-sig')

def user_to_mysql(df_new, engine):
    df_new.to_sql(name='USER', con=engine, if_exists='append', index=False)
    print("完成匯入MySQL")