from pyrogram import Client
from pyrogram.types import Message, CallbackQuery
from utils.keyboards import kb_start, kb_main_menu
from utils.state import clear_state

WELCOME_TEXT = """
🌟 **Telegram Vault Bot**

Apne multiple Telegram accounts ko securely manage karo.

Sessions sirf tumhari local machine par save hote hain — kahin aur nahi.

👇 Niche button press karo shuru karne ke liye:
"""

MAIN_MENU_TEXT = """
🏠 **Main Menu**

Kya karna chahte ho?
"""


async def cmd_start(client: Client, message: Message):
    clear_state(message.from_user.id)
    
    await message.reply_photo(
        photo="assets/start.jpg",  
        caption=WELCOME_TEXT,
        reply_markup=kb_start()
    )


async def cb_main_menu(client: Client, callback: CallbackQuery):
    clear_state(callback.from_user.id)
    await callback.message.edit_text(
        MAIN_MENU_TEXT,
        reply_markup=kb_main_menu()
    )
