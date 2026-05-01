from pyrogram import Client
from pyrogram.types import Message, CallbackQuery
from utils.keyboards import kb_start, kb_main_menu
from utils.state import clear_state
from pyrogram.enums import ParseMode

WELCOME_TEXT = """
<blockquote expandable>⚖️ <u>𝗞𝗔𝗥𝗠𝗔 𝗠𝗔𝗦𝗦 𝗥𝗘𝗣𝗢𝗥𝗧𝗘𝗥</u> ⚖️</blockquote>
<blockquote><b>💀 𝐀 ᴘᴏᴡᴇʀғᴜʟ sʏsᴛᴇᴍ ᴛᴏ ᴀᴄᴄᴜʀᴀᴛᴇʟʏ ʙᴀɴ ᴀɴʏᴏɴᴇ's 𝐓ᴇʟᴇɢʀᴀᴍ ᴀᴄᴄᴏᴜɴᴛ ʙʏ ʙᴜʟᴋ ʀᴇᴘᴏʀᴛɪɴɢ ᴛʜᴇᴍ.</b></blockquote>
<blockquote expandable><b>⚡ 𝐅ᴀsᴛ • 𝐀ᴜᴛᴏᴍᴀᴛᴇᴅ • 𝐄ғғɪᴄɪᴇɴᴛ.</b>
<b>🔒 𝐒ᴇᴄᴜʀᴇ & 𝐏ʀɪᴠᴀᴛᴇ 𝐒ᴇssɪᴏɴs.</b>
<b>📊 𝐂ʟᴇᴀɴ • 𝐒ɪᴍᴘʟᴇ • 𝐔sᴇʀ - 𝐅ʀɪᴇɴᴅʟʏ</b></blockquote>
<blockquote expandable><b>⚠️ 𝚄𝚜𝚎 𝚛𝚎𝚜𝚙𝚘𝚗𝚜𝚒𝚋𝚕𝚢 — 𝙰𝚌𝚝𝚒𝚘𝚗𝚜 𝚑𝚊𝚟𝚎 𝚌𝚘𝚗𝚜𝚎𝚚𝚞𝚎𝚗𝚌𝚎𝚜.</b></blockquote>
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
        parse_mode=ParseMode.HTML,
        reply_markup=kb_start()
    )


async def cb_main_menu(client: Client, callback: CallbackQuery):
    clear_state(callback.from_user.id)
    await callback.message.edit_text(
        MAIN_MENU_TEXT,
        reply_markup=kb_main_menu()
    )
