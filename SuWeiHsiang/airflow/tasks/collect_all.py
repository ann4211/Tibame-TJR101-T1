import pandas as pd
import time

from utils.collect_one import one_restaurant_comments
from utils.save_error import save_error_info

from airflow.decorators import task

@task
def all_restaurants_comments(start,end):
    df = pd.read_csv(f"./data/restaurants.csv")
    count = 1
    if end == "" : end = df.shape[0]
    for name,link in zip(df.iloc[start:end,0],df.iloc[start:end,2]) :
        print(f"爬取第{start + count}家評價，尚餘{end - start - count}家待爬取")
        try :
            one_restaurant_comments(name,link)
        except Exception as e:
            save_error_info(name,start,count,e)
        
        time.sleep(1)
        count += 1