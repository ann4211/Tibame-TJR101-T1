import pendulum
from airflow.decorators import dag, task
import pymysql
import pandas as pd

def conn_mysql():
    return pymysql.connect(
        host='35.194.188.197',
        port=3306,
        user='user',
        password='password',
        db='BWA',
        charset='utf8mb4',
        autocommit=True
    )

# Define the DAG
@dag(
    schedule="30 14 * * *",
    start_date=pendulum.datetime(2025, 5, 20, tz="UTC"),
    catchup=False,
    tags=["step 3 : update exist user information"],
)

def d_04_update_user():

    @task
    def read_csv():
        df = pd.read_csv("./data/update_user.csv")
        return df.to_dict(orient='list')
    
    @task
    def update_user(data_dict):
        df = pd.DataFrame(data_dict)
        conn = conn_mysql()
        with conn.cursor() as cursor:
            sql = """
                update USER
                set
                    is_local_guide = %s,
                    review_count = %s,
                    photo_count = %s
                where
                    user_id = %s
            """
            data = [
                (is_local_guide, review_count, photo_count, user_id)
                for is_local_guide, review_count, photo_count, user_id in zip(
                    df['is_local_guide'],
                    df['review_count'],
                    df['photo_count'],
                    df['user_id']
                )
            ]

            cursor.executemany(sql, data)
        conn.close()
    
    update_user(read_csv())
    
d_04_update_user()