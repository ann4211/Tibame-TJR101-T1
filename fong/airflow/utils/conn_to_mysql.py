from sqlalchemy import create_engine

def conn_to_mysql():

    host = '35.194.188.197'
    port = 3306
    user = 'user'
    password = 'password'
    db = 'BWA'

    engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{db}')
    print("成功連線上MySQL")
    return engine