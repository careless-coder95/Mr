import asyncio
from pyrogram import Client
from pyrogram.types import Message, CallbackQuery
from pyrogram.errors import (
    PhoneNumberInvalid, PhoneCodeInvalid, PhoneCodeExpired,
    SessionPasswordNeeded, PasswordHashInvalid, FloodWait
)
from utils.keyboards import kb_after_add, kb_main_menu, kb_back_main
from utils.state import set_state, get_state, update_data, clear_state
from database.db import save_account
import os
from pyrogram.enums import ParseMode

# Temporary clients dict for login sessions
_login_clients: dict = {}


async def cb_add_account(client: Client, callback: CallbackQuery):
    uid = callback.from_user.id
    clear_state(uid)
    set_state(uid, "awaiting_phone")
    await callback.message.edit_text(
        "<blockquote>"
        "📱 **Enter the phone number**\n\n"
        "Write with country code:\n"
        "Example: `+919XXXXXXXXX`\n\n"
        "🚫 To cancel, write /cancel."
        "</blockquote>",
        parse_mode=ParseMode.HTML,
        reply_markup=kb_back_main()
    )


async def handle_add_account_flow(client: Client, message: Message):
    uid = message.from_user.id
    state = get_state(uid)
    if not state:
        return

    step = state["step"]
    data = state["data"]
    text = message.text.strip()

    # ── Step 1: Phone number ────────────────────────────────
    if step == "awaiting_phone":
        if not text.startswith("+"):
            await message.reply("⚠️ Phone number should start with `+`.\nExample: `+919XXXXXXXXX`")
            return

        await message.reply("⏳ I am sending OTP...")

        api_id = int(os.getenv("API_ID"))
        api_hash = os.getenv("API_HASH")

        temp_client = Client(
            f"temp_{uid}",
            api_id=api_id,
            api_hash=api_hash,
            in_memory=True
        )

        try:
            await temp_client.connect()
            sent = await temp_client.send_code(text)
            _login_clients[uid] = temp_client
            update_data(uid, "phone", text)
            update_data(uid, "phone_code_hash", sent.phone_code_hash)
            set_state(uid, "awaiting_otp", data={
                "phone": text,
                "phone_code_hash": sent.phone_code_hash
            })
            await message.reply(
                "🔐 **Enter OTP**\n\n"
                "You have received an OTP on your Telegram..\n"
                "Wow, type it here:\n\n"
                "🚫 Cancel: /cancel"
            )
        except PhoneNumberInvalid:
            await temp_client.disconnect()
            await message.reply("🚫 Invalid phone number. Try again.")
            clear_state(uid)
        except FloodWait as e:
            await temp_client.disconnect()
            await message.reply(f"⏳ Flood wait: {e.value} try after seconds.")
            clear_state(uid)
        except Exception as e:
            await temp_client.disconnect()
            await message.reply(f"🚫 Error: `{e}`")
            clear_state(uid)

    # ── Step 2: OTP ─────────────────────────────────────────
    elif step == "awaiting_otp":
        temp_client = _login_clients.get(uid)
        if not temp_client:
            await message.reply("🚫 Session expired. Ok /start it.")
            clear_state(uid)
            return

        otp = text.replace(" ", "")
        phone = data["phone"]
        phone_code_hash = data["phone_code_hash"]

        try:
            await temp_client.sign_in(phone, phone_code_hash, otp)
            # Login successful (no 2FA)
            await _finish_login(client, message, uid, temp_client, phone, "")

        except SessionPasswordNeeded:
            set_state(uid, "awaiting_2fa", data={
                "phone": phone,
                "phone_code_hash": phone_code_hash
            })
            await message.reply(
                "🔑 **Enter 2FA Password**\n\n"
                "2-step verification is enabled on your account.\n"
                "🚫 Cancel: /cancel"
            )
        except PhoneCodeInvalid:
            await message.reply("🚫 Wrong OTP. Try Again.")
        except PhoneCodeExpired:
            await message.reply("🚫 OTP has expired. /start again.")
            await temp_client.disconnect()
            _login_clients.pop(uid, None)
            clear_state(uid)
        except Exception as e:
            await message.reply(f"❌ Error: `{e}`")

    # ── Step 3: 2FA Password ─────────────────────────────────
    elif step == "awaiting_2fa":
        temp_client = _login_clients.get(uid)
        if not temp_client:
            await message.reply("🚫 Session expired. /start again.")
            clear_state(uid)
            return

        phone = data["phone"]
        password = text

        try:
            await temp_client.check_password(password)
            await _finish_login(client, message, uid, temp_client, phone, password)
        except PasswordHashInvalid:
            await message.reply("🚫 Wrong password. try again.")
        except Exception as e:
            await message.reply(f"🚫 Error: `{e}`")


async def _finish_login(
    bot: Client,
    message: Message,
    uid: int,
    temp_client: Client,
    phone: str,
    password: str
):
    """Export session and save to DB."""
    try:
        session_string = await temp_client.export_session_string()
        await temp_client.disconnect()
        _login_clients.pop(uid, None)

        # Save to local JSON DB
        save_account(phone, session_string, password)
        clear_state(uid)

        await message.reply(
            "<blockquote>"
            "✅ <b>Account Successfully Saved!</b>\n\n"
            f"📱 Number: `{phone}`\n"
            "🔒 Session securely stored locally."
            "</blockquote>",
            parse_mode=ParseMode.HTML,
            reply_markup=kb_after_add()
        )

    except Exception as e:
        await message.reply(f"❌ Session save karne mein error: `{e}`")
        clear_state(uid)
