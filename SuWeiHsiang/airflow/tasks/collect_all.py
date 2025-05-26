import pandas as pd
from pathlib import Path
from typing import List, Dict

from utils.collect_one import one_restaurant_comments
from utils.save_error import save_error_info

from airflow.decorators import task
from airflow.utils.task_group import TaskGroup


@task
def create_retry_csv() -> None:
    path = Path("./data/retry.csv")
    df = pd.DataFrame(columns=["st_name", "st_url", "error"])
    df.to_csv(path, index=False, header=True, encoding="utf-8-sig")


@task
def get_restaurants_info(is_retry: bool) -> List[Dict[str, str]]:
    """
    取得店家資訊
    """
    if is_retry:
        df = pd.read_csv("./data/retry.csv")[["st_name", "st_url"]]
    else:
        df = pd.read_csv("./data/restaurants.csv")[["st_name", "st_url"]]
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
        save_error_info(st_name, st_url, e)


@task
def retry_drop_sucessful() -> None:
    path = Path("./data/retry.csv")
    df = pd.read_csv(path)
    df = df[df.duplicated(subset=["st_url"], keep=False)]
    df.to_csv(path, index=False, header=True, encoding="utf-8-sig")


def create_group(batch_num: int, restaurants: List[Dict[str, str]]) -> TaskGroup:
    """
    建立Task Group，一個店家之新評論蒐集為一個Task
    """
    with TaskGroup(group_id=f"collect_comments_group_{batch_num}") as group:
        all_restaurants_comments.expand(restaurant=restaurants)
    return group
