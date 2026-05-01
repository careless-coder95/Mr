import os
import asyncio
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from dotenv import load_dotenv

load_dotenv()

from handlers.start import cmd_start, cb_main_menu
from handlers.add_account import cb_add_account, handle_add_account_flow
from handlers.accounts import cb_list_accounts, cb_account_detail, cb_delete_account
from handlers.target import (
    cb_target_menu, cb_set_target, handle_target_flow,
    cb_save_target, cb_delete_target
)
from handlers.love import cb_start_love, handle_love_flow
from handlers.cancel import cmd_cancel
from utils.state import get_state

# ── Bot client ────────────────────────────────────────────────
bot = Client(
    "vault_bot",
    bot_token=os.getenv("BOT_TOKEN"),
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH"),
)

# ── Message router: decides which flow handles the message ────
async def message_router(client: Client, message):
    uid = message.from_user.id
    state = get_state(uid)
    if not state:
        return

    step = state["step"]

    if step in ("awaiting_phone", "awaiting_otp", "awaiting_2fa"):
        await handle_add_account_flow(client, message)

    elif step == "awaiting_target_input":
        await handle_target_flow(client, message)

    elif step in ("awaiting_love_reason", "awaiting_love_count"):
        await handle_love_flow(client, message)


# ── Register handlers ─────────────────────────────────────────

# Commands
bot.add_handler(MessageHandler(cmd_start,  filters.command("start") & filters.private))
bot.add_handler(MessageHandler(cmd_cancel, filters.command("cancel") & filters.private))

# Message flow router (catch-all for stateful conversations)
bot.add_handler(MessageHandler(
    message_router,
    filters.text & filters.private & ~filters.command(["start", "cancel"])
))

# Callback queries
bot.add_handler(CallbackQueryHandler(cb_main_menu,      filters.regex("^main_menu$")))
bot.add_handler(CallbackQueryHandler(cb_add_account,    filters.regex("^add_account$")))
bot.add_handler(CallbackQueryHandler(cb_list_accounts,  filters.regex("^list_accounts$")))
bot.add_handler(CallbackQueryHandler(cb_account_detail, filters.regex("^account_detail:")))
bot.add_handler(CallbackQueryHandler(cb_delete_account, filters.regex("^delete_account:")))
bot.add_handler(CallbackQueryHandler(cb_target_menu,    filters.regex("^target_menu$")))
bot.add_handler(CallbackQueryHandler(cb_set_target,     filters.regex("^set_target$")))
bot.add_handler(CallbackQueryHandler(cb_save_target,    filters.regex("^save_target$")))
bot.add_handler(CallbackQueryHandler(cb_delete_target,  filters.regex("^delete_target$")))
bot.add_handler(CallbackQueryHandler(cb_start_love,     filters.regex("^start_love$")))


if __name__ == "__main__":
    print("🚀 Vault Bot starting...")
    bot.run()
