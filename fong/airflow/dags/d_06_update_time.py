import pendulum
from airflow.decorators import dag, task
import pymysql

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
    schedule="30 15 * * *",
    start_date=pendulum.datetime(2025, 5, 20, tz="UTC"),
    catchup=False,
    tags=["step 6 : update time imformation everyday"],
)

def d_06_update_time():
    # 跟名稱長得一樣

    @task
    # 變成airflow的task物件
    def update_user():
        conn = conn_mysql()
        with conn.cursor() as cursor:
            cursor.execute("""
                update USER
                set update_date = CURDATE();
            """)
        conn.close()

    @task
    def update_comment():
        conn = conn_mysql()
        with conn.cursor() as cursor:
            cursor.execute("""
                update COMMENT
                set update_date = CURDATE();
            """)
        conn.close()

    @task
    def update_months_ago():
        conn = conn_mysql()
        with conn.cursor() as cursor:
            cursor.execute("""
                update COMMENT
                set months_ago = months_ago + (datediff(CURDATE(), update_date)/ 30.0);
            """)
        conn.close()

    update_user()
    months_ago_task = update_months_ago()
    # 上游的task是哪一個
    update_comment().set_upstream(months_ago_task)


d_06_update_time()