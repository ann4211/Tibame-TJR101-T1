#使用官方 Python 映像檔
FROM python:3.13-slim

#設定工作目錄
WORKDIR /app

#安裝 poetry
RUN pip install poetry

#複製必要檔案
COPY pyproject.toml poetry.lock README.md ./

#安裝依賴（不建虛擬環境、也不裝目前專案）
RUN poetry config virtualenvs.create false && poetry install --no-root --no-interaction --no-ansi

#複製剩下的所有檔案
COPY . .
# 複製啟動腳本
COPY start.sh /app/start.sh

# 確保啟動腳本有執行權限
RUN chmod +x /app/start.sh

# 使用啟動腳本
CMD ["bash", "/app/start.sh"]
