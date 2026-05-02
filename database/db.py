import json
import os
from pathlib import Path


def _db_file(user_id: int) -> str:
    return f"data/user_{user_id}.json"


def _load(user_id: int) -> dict:
    Path("data").mkdir(exist_ok=True)
    db = _db_file(user_id)
    if not os.path.exists(db):
        _save(user_id, {"accounts": {}, "target": None})
    with open(db, "r") as f:
        return json.load(f)


def _save(user_id: int, data: dict):
    Path("data").mkdir(exist_ok=True)
    with open(_db_file(user_id), "w") as f:
        json.dump(data, f, indent=2)


# ─── Accounts ───────────────────────────────────────────────

def save_account(user_id: int, phone: str, session: str, password: str = ""):
    data = _load(user_id)
    data["accounts"][phone] = {
        "phone":    phone,
        "session":  session,
        "password": password
    }
    _save(user_id, data)


def get_all_accounts(user_id: int) -> dict:
    return _load(user_id)["accounts"]


def get_account(user_id: int, phone: str) -> dict | None:
    return _load(user_id)["accounts"].get(phone)


def delete_account(user_id: int, phone: str):
    data = _load(user_id)
    data["accounts"].pop(phone, None)
    _save(user_id, data)


def count_accounts(user_id: int) -> int:
    return len(_load(user_id)["accounts"])


# ─── Target ─────────────────────────────────────────────────

def save_target(user_id: int, info: dict):
    data = _load(user_id)
    data["target"] = info
    _save(user_id, data)


def get_target(user_id: int) -> dict | None:
    return _load(user_id).get("target")


def delete_target(user_id: int):
    data = _load(user_id)
    data["target"] = None
    _save(user_id, data)
