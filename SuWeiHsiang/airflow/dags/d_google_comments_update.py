from airflow.decorators import dag,task
from tasks.collect_all import all_restaurants_comments

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
    dag_id="d_google_comments_update",
    default_args=default_args,
    description="get new google map restaurants comment daily",
    schedule_interval="0 1 * * *",
    start_date=datetime(2025,5,3),
    catchup=False
)

def d_google_comments_update():

    all_restaurants_comments(0,"")

d_google_comments_update()