from airflow.decorators import task
import pandas as pd
from datetime import date

from utils.add_comment_to_mysql import add_comment_to_mysql


@task
def send_comment_to_mysql():
    df = pd.read_csv(f"./data/Clean/comments_Cleaned.csv")
    df_yesterday = pd.read_csv("./data/comment_list.csv")
    df_nightmarket = pd.read_csv("./data/nightmarket_list.csv")
    df_store = pd.read_csv("./data/store_list.csv")
    add_comment_to_mysql(df, df_yesterday, df_nightmarket, df_store)