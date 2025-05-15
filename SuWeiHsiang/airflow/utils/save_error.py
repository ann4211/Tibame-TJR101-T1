from datetime import datetime
from pathlib import Path

def save_error_info(name,e):
    print(f"爬取{name}時發生錯誤")
    directory = Path("./data/Crawler")
    directory.mkdir(parents=True,exist_ok=True)
    path = Path(f"{directory}/log.txt")
    with open(path,"a",encoding='utf-8-sig') as f:
        f.write(f"{datetime.now().replace(microsecond=0)} : ")
        f.write(f"爬取{name}時發生錯誤\n{e}\n")
        f.close()