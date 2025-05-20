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
    schedule="0 2 * * *",
    start_date=pendulum.datetime(2025, 5, 13, tz="UTC"),
    catchup=False,
    tags=["step 9 : put analysis result back to MySQL"]
)

def d_09_return_to_comment():
    # 跟名稱長得一樣
    @task
    def read_csv():
        df = pd.read_csv("./data/comment_analysis_result.csv")
        return df.to_dict(orient="list")

    @task
    def type_change(data_dict):
        df = pd.DataFrame(data_dict)
        df['fake_comment'] = df['fake_comment'].map({'T' : True, 'F' : False})
        df['fake_comment'] = df['fake_comment'].astype(bool)
        df['fake_level'] = df['fake_level'].fillna(0).astype(int)
        return df.to_dict(orient="list")
    
    @task
    # 變成airflow的task物件
    def comment_to_mysql(data_dict):
        df = pd.DataFrame(data_dict)
        df = df.where(pd.notnull(df), None)
        conn = conn_mysql()
        with conn.cursor() as cursor:
            sql = """
                update COMMENT
                set
                    fake_comment = %s,
                    fake_level = %s,
                    fake_reason = %s
                where
                    comment_id = %s
            """
            data = [
                (fake_comment, fake_level, fake_reason, comment_id)
                for comment_id, fake_comment, fake_level, fake_reason in zip(
                    df['comment_id'],
                    df['fake_comment'],
                    df['fake_level'],
                    df['fake_reason']
                )
            ]
            cursor.executemany(sql, data)
        conn.close()

    comment_to_mysql(type_change(read_csv()))
    
d_09_return_to_comment()