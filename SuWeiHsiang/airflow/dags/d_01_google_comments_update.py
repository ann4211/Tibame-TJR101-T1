from airflow.decorators import dag
from tasks.collect_all import get_restaurants_info,get_batch_restaurant,create_group

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
    dag_id="d_01_google_comments_update",
    default_args=default_args,
    description="get new google map restaurants comment daily",
    max_active_tasks=3,
    schedule_interval="0 1 * * *",
    start_date=datetime(2025,5,3),
    catchup=False,
    tags=["Step 1 : update comments from all restaurant"]
)

def d_01_google_comments_update():
    
    restaurants = get_restaurants_info()
    batch1 = get_batch_restaurant.override(task_id="get_batch_0")(restaurants,0,1000)
    batch2 = get_batch_restaurant.override(task_id="get_batch_1")(restaurants,1,1000)
    create_group(1,batch1)
    create_group(2,batch2)
        
d_01_google_comments_update()