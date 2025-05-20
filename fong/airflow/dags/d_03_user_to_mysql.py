from airflow.decorators import dag
from datetime import datetime, timedelta
from tasks.send_user_to_mysql import send_user_to_mysql


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email": ["your_email@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

@dag(
    dag_id="d_03_user_to_mysql",
    default_args=default_args,
    description="put new user to mysql",
    schedule_interval="0 14 * * *",
    start_date=datetime(2025,5,20),
    catchup=False,
    tags=["step 4 : add new user today"]
)

def user_to_mysql():
    send_user_to_mysql()
    
user_to_mysql()
