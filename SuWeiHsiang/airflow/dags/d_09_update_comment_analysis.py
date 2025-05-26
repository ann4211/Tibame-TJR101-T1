from airflow.decorators import dag, task
from tasks.task_notify import task_start_notify, task_finish_notify
from utils.send_tele_message import send_failure_message
from utils.update_comment_analysis import main

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
    dag_id="d_09_update_comment_analysis",
    default_args=default_args,
    description="analysis comment fake or truth daily",
    schedule_interval="10 1 * * *",
    start_date=datetime(2025, 5, 17),
    catchup=False,
    tags=["step 9 : update comment analysis"],
)
def d_09_update_comment_analysis():
    @task
    def start_analysis():
        main()

    start = task_start_notify()
    analysis = start_analysis()
    finish = task_finish_notify()

    start >> analysis >> finish


d_09_update_comment_analysis()
