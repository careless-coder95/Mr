from pyrogram import Client
from pyrogram.types import CallbackQuery
from utils.keyboards import kb_accounts_list, kb_account_detail, kb_main_menu
from database.db import get_all_accounts, delete_account


async def cb_list_accounts(client: Client, callback: CallbackQuery):
    accounts = get_all_accounts()

    if not accounts:
        await callback.message.edit_text(
            "📂 **Accounts**\n\n"
            "❌ Koi account saved nahi hai.\n"
            "➕ Add Account se pehle account add karo.",
            reply_markup=kb_main_menu()
        )
        return

    phones = list(accounts.keys())
    await callback.message.edit_text(
        f"📂 **Your Saved Accounts** ({len(phones)})\n\n"
        "Kisi account pe click karo details dekhne ke liye:",
        reply_markup=kb_accounts_list(phones)
    )


async def cb_account_detail(client: Client, callback: CallbackQuery):
    phone = callback.data.split(":", 1)[1]
    from database.db import get_account
    acc = get_account(phone)

    if not acc:
        await callback.answer("Account nahi mila!", show_alert=True)
        return

    password_display = "✅ Set hai" if acc.get("password") else "❌ Nahi hai"

    await callback.message.edit_text(
        f"📱 **Account Details**\n\n"
        f"📱 Number: `{acc['phone']}`\n"
        f"🔑 2FA: {password_display}\n"
        f"🔒 Session: Saved ✅",
        reply_markup=kb_account_detail(phone)
    )


async def cb_delete_account(client: Client, callback: CallbackQuery):
    phone = callback.data.split(":", 1)[1]
    delete_account(phone)
    await callback.answer("✅ Account delete ho gaya!", show_alert=True)

    # Refresh list
    accounts = get_all_accounts()
    phones = list(accounts.keys())

    if not phones:
        await callback.message.edit_text(
            "📂 **Your Accounts**\n\n"
            "❌ Koi account nahi bacha.",
            reply_markup=kb_main_menu()
        )
    else:
        await callback.message.edit_text(
            f"📂 **Your Saved Accounts** ({len(phones)})\n\n"
            "Kisi account pe click karo details dekhne ke liye:",
            reply_markup=kb_accounts_list(phones)
        )
