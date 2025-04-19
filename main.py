from flask import Flask, request
import os
import requests

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

@app.route("/", methods=["GET"])
def health():
    return "OK", 200

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        reply = f"📌 收到了喔！你剛剛說：「{text}」"
        requests.post(f"{API_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": reply
        })
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
