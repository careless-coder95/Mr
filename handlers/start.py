from pyrogram import Client
from pyrogram.types import Message, CallbackQuery
from utils.keyboards import kb_start, kb_main_menu
from utils.state import clear_state
from pyrogram.enums import ParseMode

WELCOME_TEXT = """
<blockquote expandable>⚖️ <u>𝗞𝗔𝗥𝗠𝗔 𝗠𝗔𝗦𝗦 𝗥𝗘𝗣𝗢𝗥𝗧𝗘𝗥</u> ⚖️</blockquote>
<blockquote><b>💀 𝐀 ᴘᴏᴡᴇʀғᴜʟ sʏsᴛᴇᴍ ᴛᴏ ᴀᴄᴄᴜʀᴀᴛᴇʟʏ ʙᴀɴ ᴀɴʏᴏɴᴇ's ᴛᴇʟᴇɢʀᴀᴍ ᴀᴄᴄᴏᴜɴᴛ ʙʏ ʙᴜʟᴋ ʀᴇᴘᴏʀᴛɪɴɢ ᴛʜᴇᴍ.</b></blockquote>
<blockquote expandable><b>⚡ ꜰᴀsᴛ • ᴀᴜᴛᴏᴍᴀᴛᴇᴅ • ᴇғғɪᴄɪᴇɴᴛ.</b>
<b>🔒 sᴇᴄᴜʀᴇ & ᴘʀɪᴠᴀᴛᴇ sᴇssɪᴏɴs.</b>
<b>📊 cʟᴇᴀɴ • sɪᴍᴘʟᴇ • ᴜsᴇʀ - ꜰʀɪᴇɴᴅʟʏ</b></blockquote>
<blockquote expandable><b>⚠️ 𝚄𝚜𝚎 𝚛𝚎𝚜𝚙𝚘𝚗𝚜𝚒𝚋𝚕𝚢 — 𝙰𝚌𝚝𝚒𝚘𝚗𝚜 𝚑𝚊𝚟𝚎 𝚌𝚘𝚗𝚜𝚎𝚚𝚞𝚎𝚗𝚌𝚎𝚜.</b></blockquote>
"""

MAIN_MENU_TEXT = """
<blockquote expandable><b>❖ <u>𝙼𝙴𝚃𝙷𝙾𝙳 𝙾𝙵 𝚁𝙴𝙿𝙾𝚃𝙸𝙽𝙶</u> :</b></blockquote>
<blockquote expandable><b>➥ 𝐅ɪʀsᴛ, ᴀᴅᴅ ᴀ ᴍɪɴɪᴍᴜᴍ ᴏғ 10 ᴀᴄᴄᴏᴜɴᴛs.</b>
<b>➥ 𝐓ʜᴇɴ sᴇʟᴇᴄᴛ ʏᴏᴜʀ ᴛᴀʀɢᴇᴛ ᴀɴᴅ sᴛᴀʀᴛ ʀᴇᴘᴏʀᴛɪɴɢ.</b></blockquote>
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
        parse_mode=ParseMode.HTML,
        reply_markup=kb_main_menu()
    )
