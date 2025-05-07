FROM apache/airflow:2.10.5-python3.12

USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         vim \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
wget gnupg2 curl unzip fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 \
libatk1.0-0 libcups2 libdbus-1-3 libgdk-pixbuf2.0-0 libnspr4 libnss3 libx11-xcb1 \
libxcomposite1 libxdamage1 libxrandr2 xdg-utils --no-install-recommends && \
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
apt-get update && apt-get install -y google-chrome-stable && \
rm -rf /var/lib/apt/lists/*

USER airflow

COPY pyproject.toml poetry.lock .
RUN touch README.md

RUN pip install apache-airflow==${AIRFLOW_VERSION}
RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry install --no-root