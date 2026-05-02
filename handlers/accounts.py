from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.types import CallbackQuery
from utils.keyboards import kb_accounts_list, kb_account_detail, kb_main_menu
from database.db import get_all_accounts, delete_account


async def cb_list_accounts(client: Client, callback: CallbackQuery):
    accounts = get_all_accounts(callback.from_user.id)
    
    if not accounts:
        await callback.message.edit_text(
            "<blockquote>"
            "📂 <u>𝗔𝗖𝗖𝗢𝗨𝗡𝗧𝗦 </u>\n\n"
            "<b>🚫 No account is saved.</b>\n"
            "<b>➕ Add an account first</b> "
            "</blockquote>",
            parse_mode=ParseMode.HTML,
            reply_markup=kb_main_menu()
        )
        return

    phones = list(accounts.keys())
    await callback.message.edit_text(
        f"<blockquote>"
        "📂 <b><u>𝗬𝗼𝘂𝗿 𝗦𝗮𝘃𝗲𝗱 𝗔𝗰𝗰𝗼𝘂𝗻𝘁𝘀</u></b>\n"
        "<b>Click on any account to view details:</b>"
        "</blockquote>",
        parse_mode=ParseMode.HTML,
        reply_markup=kb_accounts_list(phones)
    )


async def cb_account_detail(client: Client, callback: CallbackQuery):
    phone = callback.data.split(":", 1)[1]
    from database.db import get_account
    acc = get_account(phone)

    if not acc:
        await callback.answer("Account not found!", show_alert=True)
        return

    password_display = "✅ Set" if acc.get("password") else "🚫 Not Available"

    await callback.message.edit_text(
        f"<blockquote>"
        f"📱 <u>𝗔𝗖𝗖𝗢𝗨𝗡𝗧 𝗗𝗘𝗧𝗔𝗜𝗟𝗦</u>\n"
        f"<b>📱 Number:</b> {acc['phone']}\n"
        f"<b>🔑 2FA:</b> {password_display}\n"
        f"<b>🔒 Session: Saved ✅</b>"
        f"</blockquote>",
        parse_mode=ParseMode.HTML,
        reply_markup=kb_account_detail(phone)
    )


async def cb_delete_account(client: Client, callback: CallbackQuery):
    phone = callback.data.split(":", 1)[1]
    delete_account(phone)
    await callback.answer("✅ Account deleted!", show_alert=True)

    # Refresh list
    accounts = get_all_accounts()
    phones = list(accounts.keys())

    if not phones:
        await callback.message.edit_text(
            "<blockquote>"
            "📂 <u>𝗬𝗼𝘂𝗿 𝗔𝗰𝗰𝗼𝘂𝗻𝘁𝘀</u>\n"
            "<b>🚫 No account left.</b>"
            "</blockquote>",
            parse_mode=ParseMode.HTML,
            reply_markup=kb_main_menu()
        )
    else:
        await callback.message.edit_text(
            f"<blockquote>"
            "📂 <u>𝗬𝗼𝘂𝗿 𝗦𝗮𝘃𝗲𝗱 𝗔𝗰𝗰𝗼𝘂𝗻𝘁𝘀</u> ({len(phones)})\n"
            "<b>Click on any account to view details:</b>"
            "</blockquote>",
            parse_mode=ParseMode.HTML,
            reply_markup=kb_accounts_list(phones)
        )
