from flask import Flask, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

user_sessions = {}

def send_message(chat_id, text, reply_markup=None):
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        data["reply_markup"] = reply_markup
    requests.post(f"{API_URL}/sendMessage", json=data)

def answer_callback(callback_id, text=None):
    data = {"callback_query_id": callback_id}
    if text:
        data["text"] = text
        data["show_alert"] = False
    requests.post(f"{API_URL}/answerCallbackQuery", json=data)

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if "callback_query" in data:
        callback = data["callback_query"]
        chat_id = str(callback["message"]["chat"]["id"])
        callback_id = callback["id"]
        data_payload = callback["data"]

        if data_payload.startswith("book_"):
            time = data_payload.split("_", 1)[1]
            send_message(chat_id, f"✅ Your session at {time} is booked!")
            send_message(ADMIN_ID, f"📩 New booking from {chat_id}: {time}")
            answer_callback(callback_id, f"Booked at {time}")
        return "OK"

    message = data.get("message", {})
    chat_id = str(message.get("chat", {}).get("id", ""))
    text = message.get("text", "").strip()

    if text == "/start":
        keyboard = {
            "keyboard": [
                ["📋 Membership Plans", "📅 Book a Session"],
                ["🕐 Opening Hours", "📞 Contact Info"]
            ],
            "resize_keyboard": True
        }
        send_message(chat_id, "🏋️‍♂️ Welcome to IronPulse Gym!
How can I help you today?", reply_markup=keyboard)

    elif text == "📋 Membership Plans":
        msg = "<b>🏷️ Membership Plans:</b>\n\n💪 Basic - 80dt/month\n🔥 Premium - 120dt/month\n🧑‍🏫 With Trainer - 180dt/month"
        send_message(chat_id, msg)

    elif text == "📅 Book a Session":
        keyboard = {
            "inline_keyboard": [
                [{"text": "Monday 10AM", "callback_data": "book_Monday 10AM"}],
                [{"text": "Wednesday 6PM", "callback_data": "book_Wednesday 6PM"}],
                [{"text": "Friday 5PM", "callback_data": "book_Friday 5PM"}]
            ]
        }
        send_message(chat_id, "📅 Choose a time to book your session:", reply_markup=keyboard)

    elif text == "🕐 Opening Hours":
        send_message(chat_id, "🕐 We are open:
Mon-Sat: 6am - 10pm
Sun: Closed")

    elif text == "📞 Contact Info":
        send_message(chat_id, "📞 Phone: +216 99 123 456
📍 Address: 123 Fitness St, Tunis")

    else:
        send_message(chat_id, "❓ I didn’t understand that. Please use the buttons.")

    return "OK"

if __name__ == "__main__":
    app.run(debug=True)
