import os

# Bot Token (Get from @BotFather)
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# Admin User ID (Your Telegram ID)
ADMIN_ID = 123456789  # Replace with your user ID

# Database
DB_NAME = "reporter.db"

# Sessions directory
SESSIONS_DIR = "sessions"

# Rate limiting
REPORT_DELAY = 10  # seconds between reports per session
MAX_REPORTS_PER_ID = 3  # max reports per 10 seconds per ID

# Reporting reasons
REPORT_REASONS = {
    "Hate Speech": "This content contains hate speech and violates Telegram's Terms of Service.",
    "Copyright Violation": "This content violates copyright laws and intellectual property rights.",
    "Scam/Fraud": "This is a scam/fraudulent content targeting users for financial gain.",
    "Child Abuse": "This content involves child abuse material and is illegal.",
    "Pornography/Adult Content": "This contains pornography/adult content posted without consent."
}
