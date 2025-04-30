# 使用官方 Python 映像檔
FROM python:3.12.10

# 設定工作目錄
WORKDIR /app

# 安裝系統需要的工具
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# 設定環境變數，讓 selenium 找到 chrome 路徑
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER=/usr/bin/chromedriver

# 安裝 Google Chrome 瀏覽器
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable

# 清理 /tmp 目錄
RUN rm -rf /tmp/*

# 安裝 dos2unix 工具
RUN apt-get update && apt-get install -y dos2unix

# 安裝 poetry
RUN pip install poetry

# 複製必要檔案
COPY pyproject.toml poetry.lock README.md ./

# 安裝依賴（不建虛擬環境、不裝自己）
RUN poetry config virtualenvs.create false && poetry install --no-root --no-interaction --no-ansi

# 複製剩下的所有檔案
COPY . .

# 複製啟動腳本
COPY start.sh /app/start.sh

# 確保啟動腳本有執行權限
RUN chmod +x /app/start.sh

# 修正 start.sh 的換行符號
RUN dos2unix /app/start.sh

# 使用啟動腳本
CMD ["bash", "/app/start.sh"]
