import pandas as pd
from typing import List, Dict

from utils.collect_one import one_restaurant_comments
from utils.save_error import save_error_info

from airflow.decorators import task
from airflow.utils.task_group import TaskGroup


@task
def get_restaurants_info() -> List[Dict[str, str]]:
    """
    取得店家資訊
    """
    df = pd.read_csv("./data/restaurants.csv", encoding="utf-8-sig")[
        ["st_name", "st_url"]
    ]
    return df.to_dict(orient="records")


@task
def get_batch_restaurant(
    restaurants: List[Dict[str, str]], batch_num: int, batch_size: int
) -> List[Dict[str, str]]:
    """
    將店家進行分組
    """
    start = batch_size * batch_num
    end = start + batch_size
    return restaurants[start:end]


@task
def all_restaurants_comments(restaurant: Dict[str, str]) -> None:
    """
    逐店家進行新評論蒐集
    """
    st_name = restaurant["st_name"]
    st_url = restaurant["st_url"]
    print(f"正在爬取{st_name}的評論")
    try:
        one_restaurant_comments(st_name, st_url)
    except Exception as e:
        save_error_info(st_name, e)


def create_group(batch_num: int, restaurants: List[Dict[str, str]]) -> None:
    """
    建立Task Group，一個店家之新評論蒐集為一個Task
    """
    with TaskGroup(group_id=f"collect_comments_group_{batch_num}") as group:
        all_restaurants_comments.expand(restaurant=restaurants)
