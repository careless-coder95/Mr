from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.types import CallbackQuery
from utils.keyboards import kb_accounts_list, kb_account_detail, kb_main_menu
from database.db import get_all_accounts, delete_account


async def cb_list_accounts(client: Client, callback: CallbackQuery):
    accounts = get_all_accounts()

    if not accounts:
        await callback.message.edit_text(
            "<blockquote>"
            "📂 <b><u>Accounts</u></b>\n\n"
            "❌ No account is saved.\n"
            "➕ Add an account first "
            "</blockquote>",
            parse_mode=ParseMode.HTML,
            reply_markup=kb_main_menu()
        )
        return

    phones = list(accounts.keys())
    await callback.message.edit_text(
        f"<blockquote>"
        "📂 <b><u>Your Saved Accounts</u></b>\n\n"
        "Click on any account to view details:"
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
        f"📱 <b><u>Account Details</u></b>\n\n"
        f"📱 Number: `{acc['phone']}`\n"
        f"🔑 2FA: {password_display}\n"
        f"🔒 Session: Saved ✅"
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
            "📂 <b><u>Your Accounts</u></b>\n\n"
            "❌ No account left."
            "</blockquote>",
            parse_mode=ParseMode.HTML,
            reply_markup=kb_main_menu()
        )
    else:
        await callback.message.edit_text(
            f"<blockquote>"
            "📂 <b>Your Saved Accounts</b> ({len(phones)})\n\n"
            "Click on any account to view details:"
            "</blockquote>",
            parse_mode=ParseMode.HTML,
            reply_markup=kb_accounts_list(phones)
        )
