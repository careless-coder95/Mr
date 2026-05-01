import json
import os
from pathlib import Path

DB_FILE = "data/vault.json"

def _load() -> dict:
    Path("data").mkdir(exist_ok=True)
    if not os.path.exists(DB_FILE):
        _save({"accounts": {}, "target": None})
    with open(DB_FILE, "r") as f:
        return json.load(f)

def _save(data: dict):
    Path("data").mkdir(exist_ok=True)
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ─── Accounts ───────────────────────────────────────────────

def save_account(phone: str, session: str, password: str = ""):
    data = _load()
    data["accounts"][phone] = {
        "phone":    phone,
        "session":  session,
        "password": password
    }
    _save(data)

def get_all_accounts() -> dict:
    return _load()["accounts"]

def get_account(phone: str) -> dict | None:
    return _load()["accounts"].get(phone)

def delete_account(phone: str):
    data = _load()
    data["accounts"].pop(phone, None)
    _save(data)

def count_accounts() -> int:
    return len(_load()["accounts"])

# ─── Target ─────────────────────────────────────────────────

def save_target(info: dict):
    data = _load()
    data["target"] = info
    _save(data)

def get_target() -> dict | None:
    return _load().get("target")

def delete_target():
    data = _load()
    data["target"] = None
    _save(data)
