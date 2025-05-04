import requests
from bs4 import BeautifulSoup

from airflow.decorators import dag,task
from datetime import datetime,timedelta

import pandas as pd

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
    dag_id="d_gossiping_crawler",
    default_args=default_args,
    description="import task",
    schedule_interval="* * * * *",
    start_date=datetime(2025,4,23),
    catchup=False
)

def d_gossiping_crawler():
    @task
    def get_gossiping_article():
        web = requests.get('https://www.ptt.cc/bbs/Gossiping/index.html', cookies={'over18':'1'})
        soup = BeautifulSoup(web.text, "html.parser")
        title = soup.find_all('div', class_='title')[-6]

        with open("./data/gossiping.txt",mode="a",encoding="utf-8-sig") as f:
            f.write(title.text.lstrip("\n"))
            f.close()

    get_gossiping_article()

d_gossiping_crawler()