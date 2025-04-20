# daily_push.py
import os
import json
import gspread
import requests
from datetime import datetime
import pytz
from oauth2client.service_account import ServiceAccountCredentials

# === 初始化 Google Sheets 連線 ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(os.environ["GOOGLE_CREDS_JSON"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

BOT_TOKEN = os.environ["BOT_TOKEN"]
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# === 取得台灣時間 ===
tz = pytz.timezone("Asia/Taipei")
today = datetime.now(tz).strftime("%Y-%m-%d")

# === 抓 Sheets ===
sheet_act = client.open("任務秘書資料表").worksheet("活動")
sheet_todo = client.open("任務秘書資料表").worksheet("待辦")

records_act = sheet_act.get_all_records()
records_todo = sheet_todo.get_all_records()

# === 將資料依 chat_id 分組 ===
user_messages = {}

for row in records_act:
    if row["時間/建立時間"].startswith(today):
        chat_id = str(row["Chat ID"])
        user_messages.setdefault(chat_id, []).append(f"📆 今日活動：{row['內容']}")

for row in records_todo:
    chat_id = str(row["Chat ID"])
    user_messages.setdefault(chat_id, []).append(f"📝 待辦事項：{row['內容']}")

# === 發送訊息 ===
for chat_id, items in user_messages.items():
    message = f"📣 每日提醒：\n\n" + "\n".join(items)
    requests.post(API_URL, json={
        "chat_id": chat_id,
        "text": message
    })

print("✅ 定時推播完成")
