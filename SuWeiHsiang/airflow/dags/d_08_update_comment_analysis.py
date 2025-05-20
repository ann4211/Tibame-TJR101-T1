from airflow.decorators import dag,task
from utils.update_comment_analysis import main

from datetime import datetime,timedelta

default_args = {
    "owner":"airflow",
    "email":["your_email@example.com"],
    "email_on_failure":False,
    "email_on_retry":False,
    "retries":1,
    "retry_delay":timedelta(minutes=5)
}

@dag(
    dag_id="d_08_update_comment_analysis",
    default_args=default_args,
    description="analysis comment fake or truth daily",
    schedule_interval="10 1 * * *",
    start_date=datetime(2025,5,17),
    catchup=False,
    tags=["update comment analysis"]
)

def d_08_update_comment_analysis():
    @task
    def start_analysis():
        main()

    start_analysis()
        
d_08_update_comment_analysis()
