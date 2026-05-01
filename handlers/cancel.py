from pyrogram import Client
from pyrogram.types import Message
from utils.state import clear_state
from utils.keyboards import kb_main_menu


async def cmd_cancel(client: Client, message: Message):
    uid = message.from_user.id
    clear_state(uid)
    await message.reply(
        "❌ **Cancelled.**\n\nMain menu pe wapas aa gaye.",
        reply_markup=kb_main_menu()
    )
