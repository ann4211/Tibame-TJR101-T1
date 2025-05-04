from airflow.decorators import dag,task
from tasks.cleaned import e_load_raw_data,t_get_user_id,t_is_localguide,t_get_comment_count,t_get_photo_count,t_get_time,t_get_star,t_clean_comment,l_save_cleaned_comment

from datetime import datetime,timedelta

default_args = {
    "owner":"airflow",
    "depend_on_past":False,
    "email":["your_email@example.com"],
    "email_on_failure":False,
    "email_on_retry":False,
    "retries":1,
    "retry_delay":timedelta(minutes=5)
}

@dag(
    dag_id="d_cleaned_comments",
    default_args=default_args,
    description="cleaned restaurants comments daily",
    schedule_interval="0 9 * * *",
    start_date=datetime(2025,5,3),
    catchup=False
)

def d_cleaned_comments():
    df = e_load_raw_data()
    df = t_get_user_id(df)
    df = t_is_localguide(df)
    df = t_get_comment_count(df)
    df = t_get_photo_count(df)
    df = t_get_time(df)
    df = t_get_star(df)
    df = t_clean_comment(df)
    l_save_cleaned_comment(df)

d_cleaned_comments()