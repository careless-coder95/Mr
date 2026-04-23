import os

# Bot Token (Get from @BotFather)
BOT_TOKEN = ""

# Admin User ID (Your Telegram ID)
ADMIN_ID = 123456789  # Replace with your user ID

# Database
DB_NAME = "reporter.db"

# Sessions directory
SESSIONS_DIR = "sessions"

# Rate limiting
REPORT_DELAY = 6  # seconds between reports per session
MAX_REPORTS_PER_ID = 3  # max reports per 10 seconds per ID

# Reporting reasons
REPORT_REASONS = {
    "Hate Speech": "This content promotes hate speech, discrimination, or violence against individuals or groups, violating Telegram Terms of Service.",
    "Copyright Violation": "This content infringes on copyrighted material or intellectual property rights without authorization.",
    "Scam/Fraud": "This content is associated with fraudulent activity, phishing, or deceptive practices intended to exploit users financially.",
    "Child Abuse": "This content involves child sexual abuse material or exploitation, which is strictly illegal and prohibited.",
    "Pornography/Adult Content": "This content contains explicit adult material shared without proper consent or in violation of platform policies."
}
