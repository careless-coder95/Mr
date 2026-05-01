# 🔐 Telegram Vault Bot

Apne multiple Telegram accounts ko securely manage karo — ek private bot ke through.  
Sessions sirf tumhari **local machine / VPS** par save hote hain, kahin aur nahi.

---

## 📁 Project Structure

```
tg-vault-bot/
├── bot.py                  ← Main entry point
├── requirements.txt
├── .env.example            ← Config template
├── data/
│   └── vault.json          ← Local database (auto-created)
├── database/
│   └── db.py               ← JSON database functions
├── handlers/
│   ├── start.py            ← /start command + main menu
│   ├── add_account.py      ← Account add flow (OTP login)
│   ├── accounts.py         ← Account list & details
│   ├── target.py           ← Target set/delete
│   ├── love.py             ← Start Love feature
│   └── cancel.py           ← /cancel command
└── utils/
    ├── keyboards.py        ← All inline keyboards
    └── state.py            ← In-memory conversation state
```

---

## ⚙️ Setup Guide

### Step 1 — API ID & API HASH lena

1. Browser mein kholo: https://my.telegram.org
2. Login karo apne phone number se
3. **"API development tools"** click karo
4. Ek new app banao (name kuch bhi de sakte ho)
5. Tumhe milega:
   - `api_id` → ek number (e.g. `12345678`)
   - `api_hash` → ek string (e.g. `abc123def456...`)

---

### Step 2 — Bot Token lena (BotFather)

1. Telegram pe jaao → `@BotFather` search karo
2. `/newbot` command bhejo
3. Bot ka naam do (e.g. `My Vault Bot`)
4. Username do (e.g. `myvault_bot`) — `_bot` se khatam hona chahiye
5. Tumhe milega: `bot_token` (e.g. `123456:ABCdef...`)

---

### Step 3 — Apna User ID lena

1. Telegram pe `@userinfobot` ko message karo
2. Woh tumhara `user_id` bata dega (e.g. `987654321`)

---

### Step 4 — Project Setup

```bash
# 1. Clone ya folder mein jaao
cd tg-vault-bot

# 2. Virtual environment banao (recommended)
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
# ya Windows pe:
venv\Scripts\activate

# 3. Dependencies install karo
pip install -r requirements.txt

# 4. .env file banao
cp .env.example .env
```

---

### Step 5 — .env file fill karo

```env
BOT_TOKEN=123456:ABCdefGHIjkl...
API_ID=12345678
API_HASH=abc123def456ghi789...
OWNER_ID=987654321
```

---

### Step 6 — Bot Run karo

```bash
python3 bot.py
```

Output aana chahiye:
```
🚀 Vault Bot starting...
```

---

## 🤖 Bot Features

| Feature | Description |
|---|---|
| ➕ Add Account | Phone + OTP + optional 2FA se login karo |
| 📂 Accounts | Saved accounts list dekho, details dekho, delete karo |
| 🎯 Target | Ek user ko target save karo (username ya ID se) |
| ❤️ Start Love | Reason + count enter karo, messages print hote hain |
| /cancel | Kisi bhi flow se bahar niklo |

---

## 💾 Data Storage

Sab data `data/vault.json` mein save hota hai:

```json
{
  "accounts": {
    "+919XXXXXXXXX": {
      "phone": "+919XXXXXXXXX",
      "session": "BQA...(string session)...",
      "password": "your_2fa_pass_or_empty"
    }
  },
  "target": {
    "name": "John Doe",
    "id": 123456789,
    "username": "johndoe"
  }
}
```

> ⚠️ `data/vault.json` ko **kabhi bhi publicly share mat karo** — isme tumhare session strings hain.

---

## 🛡️ Security Notes

- Sessions sirf **tumhare server/machine** par hain
- `.env` file ko `.gitignore` mein daalo agar Git use kar rahe ho
- `data/` folder bhi `.gitignore` mein daalo

`.gitignore` example:
```
.env
data/
venv/
__pycache__/
*.session
```

---

## 🚀 VPS Deploy (Ubuntu/Debian)

```bash
# System update
sudo apt update && sudo apt upgrade -y

# Python 3.10+ install
sudo apt install python3 python3-pip python3-venv -y

# Project copy karo aur setup karo
cd ~
git clone <your-repo-url> tg-vault-bot
cd tg-vault-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env   # apni values daalo

# Background mein chalane ke liye (screen)
sudo apt install screen -y
screen -S vaultbot
python3 bot.py
# Ctrl+A phir D dabaao detach karne ke liye
```

---

## ❓ Common Errors

| Error | Solution |
|---|---|
| `PhoneNumberInvalid` | Country code sahi likho: `+91...` |
| `PhoneCodeInvalid` | Galat OTP, dobara try karo |
| `PhoneCodeExpired` | OTP expire ho gaya, /start se dobara |
| `PasswordHashInvalid` | Galat 2FA password |
| `FloodWait` | Telegram ne wait karaya, message mein time bata dega |
| `API_ID not set` | `.env` file check karo |

---

## 📝 Extra Notes

- **Start Love** feature sirf messages **print** karta hai — kuch send nahi hota
- Ek waqt mein sirf **ek target** save ho sakta hai
- Account delete karne ke liye Accounts → account pe click → 🗑 Delete
- `/cancel` kisi bhi step par kaam karta hai

---

*Built with ❤️ using Pyrogram*
