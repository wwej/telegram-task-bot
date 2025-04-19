from flask import Flask, request
import os
import requests
import re
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def classify_message(text):
    # 定義關鍵詞或日期格式
    date_keywords = ["今天", "明天", "後天", "下週", "下禮拜", "點", "下午", "早上", "上午", "晚上"]
    date_pattern = r"\d{1,2}/\d{1,2}|\d{4}-\d{1,2}-\d{1,2}|\d{1,2}月\d{1,2}日"

    # 關鍵詞比對
    for keyword in date_keywords:
        if keyword in text:
            return "活動"
    # 正規比對日期格式
    if re.search(date_pattern, text):
        return "活動"
    # 否則歸類為待辦
    return "待辦"

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json

def get_gsheet_client():
    creds_dict = json.loads(os.getenv("GOOGLE_CREDS_JSON"))
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(credentials)
    return client

def save_to_google_sheet(sheet_name, row_data):
    print(f"✅ 寫入 {sheet_name}：{row_data}")
    client = get_gsheet_client()
    sheet = client.open("任務秘書資料表").worksheet(sheet_name)
    sheet.append_row(row_data)


@app.route("/", methods=["GET"])
def health():
    return "OK", 200


@app.route("/", methods=["POST"])
def webhook():
    print("📬 收到 POST 請求")
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        classification = classify_message(text)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if classification == "活動":
            save_to_google_sheet("活動", [now, classification, text, chat_id])
        else:
            save_to_google_sheet("待辦", [now, classification, text, chat_id])

        reply = f"📌 我幫你記下來了：這是「{classification}」"
        requests.post(f"{API_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": reply
        })

    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

