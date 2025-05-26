from airflow.decorators import dag
from tasks.cleaned import (
    e_load_raw_data,
    t_get_user_id,
    t_is_localguide,
    t_get_comment_count,
    t_get_photo_count,
    t_get_time,
    t_get_star,
    t_clean_comment,
    t_adjust_columns,
    t_update_months_ago,
    l_save_cleaned_comment,
)
from tasks.task_notify import task_start_notify, task_finish_notify
from utils.send_tele_message import send_failure_message

from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "depend_on_past": False,
    "email": ["your_email@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "on_failure_callback": send_failure_message,
}


@dag(
    dag_id="d_03_cleaned_comments",
    default_args=default_args,
    description="cleaned restaurants comments daily",
    schedule_interval="0 6 * * *",
    start_date=datetime(2025, 5, 3),
    catchup=False,
    tags=["Step 3 : Data Cleaning"],
)
def d_03_cleaned_comments():
    start = task_start_notify()
    df_load = e_load_raw_data()
    df_userid = t_get_user_id(df_load)
    df_local_guide = t_is_localguide(df_userid)
    df_comment_count = t_get_comment_count(df_local_guide)
    df_photo_count = t_get_photo_count(df_comment_count)
    df_time = t_get_time(df_photo_count)
    df_star = t_get_star(df_time)
    df_comment = t_clean_comment(df_star)
    df_columns = t_adjust_columns(df_comment)
    df_months_ago = t_update_months_ago(df_columns)
    save = l_save_cleaned_comment(df_months_ago)
    finish = task_finish_notify()

    (
        start
        >> df_load
        >> df_userid
        >> df_local_guide
        >> df_comment_count
        >> df_photo_count
        >> df_time
        >> df_star
        >> df_comment
        >> df_columns
        >> df_months_ago
        >> save
        >> finish
    )


d_03_cleaned_comments()
