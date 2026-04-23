import os

# 🔑 Telegram API (my.telegram.org se lo)
API_ID = 12345678  # Tera API ID
API_HASH = "your_api_hash_here"  # Tera API Hash

# 🤖 Bot Token (@BotFather se)
BOT_TOKEN = "your_bot_token_here"

# 👤 Admin ID (@userinfobot se lo)
ADMIN_ID = 123456789  

# 📁 Folders
DB_NAME = "reporter.db"
SESSIONS_DIR = "sessions"

# ⚙️ Evasion Settings
REPORT_DELAY = 8  # Average delay
MIN_DELAY = 6
MAX_DELAY = 15
MSG_HISTORY_DEPTH = 10
MAX_MSG_IDS_PER_TARGET = 20

# 🛡️ Proxies (optional - ban faster)
PROXIES = [
    # "socks5://user:pass@ip:port",
    # Add your proxies
]

# 📝 Report Reasons
REPORT_REASONS = {
    "Hate Speech": "Promotes violence/discrimination against groups/individuals violating ToS.",
    "Copyright Violation": "Infringes copyrighted material/IP without authorization.",
    "Scam/Fraud": "Phishing/scam content designed to exploit users financially.",
    "Child Abuse": "Child sexual abuse material - STRICTLY PROHIBITED.",
    "Pornography/Adult Content": "Explicit adult content violating platform guidelines."
}
