import pandas as pd
import time

from utils.collect_one import one_restaurant_comments
from utils.save_error import save_error_info

from airflow.decorators import task
from airflow.utils.task_group import TaskGroup

@task
def get_restaurants_info():
    df = pd.read_csv(f"./data/restaurants.csv",encoding="utf-8-sig")[["st_name", "st_url"]]
    return df.to_dict(orient="records")

@task
def get_batch_store(stores,batch_num,batch_size):
    start = batch_size * batch_num
    end   = start + batch_size
    return stores[start:end]

def create_group(batch_num,store):
    with TaskGroup(group_id=f"collect_comments_group_{batch_num}") as group:
        all_restaurants_comments.expand(store=store)

@task
def all_restaurants_comments(store):
    name = store["st_name"]
    link = store["st_url"]
    print(f"正在爬取{name}的評論")
    try :
        one_restaurant_comments(name,link)
    except Exception as e:
        save_error_info(name,e)
