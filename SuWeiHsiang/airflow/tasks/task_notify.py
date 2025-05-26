from airflow.decorators import task
from airflow.operators.python import get_current_context

from datetime import datetime
from utils.send_tele_message import send_message


@task
def task_start_notify():
    context = get_current_context()
    dag_id = context["dag"].dag_id
    dag_run = context["dag_run"]
    start_time = dag_run.start_date.replace(microsecond=0)
    send_message(f"Starting {dag_id} at {start_time}")


@task
def task_finish_notify():
    context = get_current_context()
    dag_id = context["dag"].dag_id
    dag_run = context["dag_run"]
    start_time = dag_run.start_date.replace(microsecond=0)
    end_time = datetime.now(tz=dag_run.start_date.tzinfo).replace(microsecond=0)
    duration = end_time - start_time
    send_message(
        f"Finishing {dag_id} at {end_time} : totally execution time is {duration}"
    )
