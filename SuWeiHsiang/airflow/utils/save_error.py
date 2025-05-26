import pandas as pd
from datetime import datetime
from pathlib import Path


def save_error_info(st_name: str, st_url: str, e: BaseException) -> None:
    """
    發生錯誤時存取錯誤紀錄
    """
    print(f"爬取{st_name}時發生錯誤")
    df = pd.DataFrame(
        [
            {
                "st_name": st_name,
                "st_url": st_url,
                "error": str(e),
            }
        ]
    )
    df.to_csv(
        "./data/retry.csv",
        index=False,
        header=False,
        mode="a",
        encoding="utf-8-sig",
    )
