import pendulum
from airflow.decorators import dag, task
import pymysql
import pandas as pd
import csv

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
    schedule="0 1 * * *",
    start_date=pendulum.datetime(2025, 5, 13, tz="UTC"),
    catchup=False,
    tags=["step 7 : get analyzed data from MySQL"],
)

def d_07_get_comment_analysis():
    # 跟名稱長得一樣

    @task
    # 變成airflow的task物件
    def create_view():
        conn = conn_mysql()
        with conn.cursor() as cursor:
            cursor.execute("""
                create or replace view comment_analysis
                as
                SELECT comment_id,st_name,rating_star,content_clean,
                    CASE
                        WHEN is_local_guide THEN 'TRUE'
                        ELSE 'FALSE'
                    END AS local_guide,
                    months_ago
                FROM COMMENT c
                    join STORE s on c.nm_id = s.nm_id and c.st_id = s.st_id
                    join USER u on c.user_id = u.user_id
                where DATE(c.create_date) = UTC_DATE()-1;
            """)
        conn.close()

    @task
    def get_view_df() -> str:
        conn = conn_mysql()
        with conn.cursor() as cursor:
            cursor.execute("""
                select *
                from comment_analysis
            """)
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(result, columns=columns)
            df.to_csv("./data/comment_analysis.csv", index=False)
        conn.close()

    create_view() >> get_view_df()
    
d_07_get_comment_analysis()