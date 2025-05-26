from airflow.decorators import dag
from tasks.collect_all import (
    get_restaurants_info,
    get_batch_restaurant,
    create_group,
    retry_drop_sucessful,
)
from tasks.task_notify import task_start_notify, task_finish_notify
from utils.send_tele_message import send_failure_message

from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "email": ["your_email@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "on_failure_callback": send_failure_message,
}


@dag(
    dag_id="d_02_google_comments_update_retry",
    default_args=default_args,
    description="retry to get new google map restaurants comment",
    max_active_tasks=3,
    schedule_interval="0 5 * * *",
    start_date=datetime(2025, 5, 22),
    catchup=False,
    tags=["Step 2 : retry to collect comments from restaurant"],
)
def d_02_google_comments_update_retry():
    start = task_start_notify()
    restaurants = get_restaurants_info(True)
    batch = get_batch_restaurant(restaurants, 0, 1000)
    group = create_group(1, batch)
    drop = retry_drop_sucessful()
    finish = task_finish_notify()

    start >> restaurants >> batch >> group >> drop >> finish


d_02_google_comments_update_retry()
