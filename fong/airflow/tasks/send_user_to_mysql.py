from airflow.decorators import task
import pandas as pd
from datetime import date

from utils.add_user_to_mysql import add_user_to_mysql


@task
def send_user_to_mysql():
    df = pd.read_csv(f"./data/Clean/comments_Cleaned.csv")
    df_old = pd.read_csv(f"./data/user_list.csv")
    add_user_to_mysql(df, df_old)
