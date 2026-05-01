from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db import count_accounts


def kb_start():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Start Your System", callback_data="main_menu")]
    ])


def kb_main_menu():
    count = count_accounts()
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Account", callback_data="add_account")],
        [InlineKeyboardButton(f"📂 Accounts [{count}]", callback_data="list_accounts")],
        [InlineKeyboardButton("🎯 Target", callback_data="target_menu")],
        [InlineKeyboardButton("❤️ Start Love", callback_data="start_love")],
    ])


def kb_back_main():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
    ])


def kb_after_add():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add More Accounts", callback_data="add_account")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")],
    ])


def kb_accounts_list(phones: list):
    buttons = [[InlineKeyboardButton(p, callback_data=f"account_detail:{p}")] for p in phones]
    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)


def kb_account_detail(phone: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🗑 Delete Account", callback_data=f"delete_account:{phone}")],
        [InlineKeyboardButton("🔙 Back", callback_data="list_accounts")],
    ])


def kb_target_menu(has_target: bool):
    buttons = []
    if has_target:
        buttons.append([InlineKeyboardButton("🗑 Delete Target", callback_data="delete_target")])
    else:
        buttons.append([InlineKeyboardButton("🔍 Set Target", callback_data="set_target")])
    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)


def kb_target_save():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💾 Save", callback_data="save_target")],
        [InlineKeyboardButton("🔙 Back", callback_data="target_menu")],
    ])
