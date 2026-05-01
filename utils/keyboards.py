from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db import count_accounts


def kb_start():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 𝐒ᴛᴀʀᴛ 𝐘ᴏᴜʀ 𝐒ʏsᴛᴇᴍ 🚀", callback_data="main_menu")]
    ])


def kb_main_menu():
    count = count_accounts()
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✙ 𝐀ᴅᴅ 𝐀ᴄᴄᴏᴜɴᴛs ✙", callback_data="add_account")],
        [InlineKeyboardButton(f"📂 𝐀ᴄᴄᴏᴜɴᴛs [{count}]", callback_data="list_accounts")],
        [InlineKeyboardButton("🎯 𝐓ᴀʀɢᴇᴛ", callback_data="target_menu")],
        [InlineKeyboardButton("💓 𝐒ᴛᴀʀᴛ 𝐋ᴏᴠᴇ", callback_data="start_love")],
    ])


def kb_back_main():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 𝐁ᴀᴄᴋ", callback_data="main_menu")]
    ])


def kb_after_add():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✙ 𝐀ᴅᴅ 𝐌ᴏʀᴇ 𝐀ᴄᴄᴏᴜɴᴛ𝐬s ✙", callback_data="add_account")],
        [InlineKeyboardButton("🔙 𝐁ᴀᴄᴋ", callback_data="main_menu")],
    ])


def kb_accounts_list(phones: list):
    buttons = [[InlineKeyboardButton(p, callback_data=f"account_detail:{p}")] for p in phones]
    buttons.append([InlineKeyboardButton("🔙 𝐁ᴀᴄᴋ", callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)


def kb_account_detail(phone: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🗑 𝐃ᴇʟᴇᴛᴇ 𝐀ᴄᴄᴏᴜɴᴛ", callback_data=f"delete_account:{phone}")],
        [InlineKeyboardButton("🔙 𝐁ᴀᴄᴋ", callback_data="list_accounts")],
    ])


def kb_target_menu(has_target: bool):
    buttons = []
    if has_target:
        buttons.append([InlineKeyboardButton("🗑 𝐃ᴇʟᴇᴛᴇ 𝐓ᴀʀɢᴇᴛ", callback_data="delete_target")])
    else:
        buttons.append([InlineKeyboardButton("🔍 𝐒ᴇᴛ 𝐓ᴀʀɢᴇᴛ", callback_data="set_target")])
    buttons.append([InlineKeyboardButton("🔙 𝐁ᴀᴄᴋ", callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)


def kb_target_save():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💾 𝐒ᴀᴠᴇ", callback_data="save_target")],
        [InlineKeyboardButton("🔙 𝐁ᴀᴄᴋ", callback_data="target_menu")],
    ])
