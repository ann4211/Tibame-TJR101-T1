import os
import requests
from dotenv import load_dotenv

load_dotenv()
Tele_Token = os.getenv("TELEGRAM_TOKEN")
Tele_ChatID = os.getenv("TELEGRAM_CHATID")


def send_message(text: str):
    url = f"https://api.telegram.org/bot{Tele_Token}/sendMessage"
    payload = {"chat_id": Tele_ChatID, "text": text}
    resp = requests.post(url, data=payload)
    if resp.status_code != 200:
        raise Exception(f"Telegram message failed:{resp.text}")


def send_failure_message(context):
    dag_id = context["dag"].dag_id
    task_id = context["task_instance"].task_id
    send_message(f"{dag_id}的{task_id}出現錯誤")
