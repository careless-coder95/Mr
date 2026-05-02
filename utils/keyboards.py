from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db import count_accounts


def kb_start():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 𝗦𝗧𝗔𝗥𝗧 𝗬𝗢𝗨𝗥 𝗦𝗬𝗦𝗧𝗘𝗠 🚀", callback_data="main_menu")],
        [InlineKeyboardButton("📖 𝗦𝗘𝗧𝗨𝗣 𝗚𝗨𝗜𝗗𝗘 📖", callback_data="setup_guide")],
    ])


def kb_main_menu(user_id: int):
    count = count_accounts(user_id)
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✙ 𝗔𝗗𝗗 𝗔𝗖𝗖𝗢𝗨𝗡𝗧𝗦  ✙", callback_data="add_account")],
        [InlineKeyboardButton(f"📂 𝗔𝗖𝗖𝗢𝗨𝗡𝗧𝗦  [{count}] 📂", callback_data="list_accounts")],
        [InlineKeyboardButton("🎯 𝗧𝗔𝗥𝗚𝗘𝗧 🎯", callback_data="target_menu")],
        [InlineKeyboardButton("💓 𝗦𝗧𝗔𝗥𝗧 𝗟𝗢𝗩𝗘 💓", callback_data="start_love")],
    ])


def kb_back_main():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞 ", callback_data="main_menu")]
    ])


def kb_after_add():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✙ 𝗔𝗗𝗗 𝗠𝗢𝗥𝗘 𝗔𝗖𝗖𝗢𝗨𝗡𝗧𝗦  ✙", callback_data="add_account")],
        [InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞 ", callback_data="main_menu")],
    ])


def kb_accounts_list(phones: list):
    buttons = [[InlineKeyboardButton(p, callback_data=f"account_detail:{p}")] for p in phones]
    buttons.append([InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞 ", callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)


def kb_account_detail(phone: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🗑 𝗗𝗘𝗟𝗘𝗧𝗘 𝗔𝗖𝗖𝗢𝗨𝗡𝗧 ", callback_data=f"delete_account:{phone}")],
        [InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞 ", callback_data="list_accounts")],
    ])


def kb_target_menu(has_target: bool):
    buttons = []
    if has_target:
        buttons.append([InlineKeyboardButton("🗑 𝗗𝗘𝗟𝗘𝗧𝗘 𝗔𝗖𝗖𝗢𝗨𝗡𝗧 ", callback_data="delete_target")])
    else:
        buttons.append([InlineKeyboardButton("🔍𝗦𝗘𝗧 𝗧𝗔𝗥𝗚𝗘𝗧", callback_data="set_target")])
    buttons.append([InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞 ", callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)


def kb_target_save():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💾 𝗦𝗔𝗩𝗘", callback_data="save_target")],
        [InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞 ", callback_data="target_menu")],
    ])

def kb_setup_guide():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞", callback_data="back_to_start")],
    ])
