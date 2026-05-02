from pyrogram import Client
from pyrogram.types import Message, CallbackQuery
from utils.keyboards import kb_start, kb_main_menu
from utils.state import clear_state
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.types import InputMediaPhoto

WELCOME_TEXT = """
<blockquote expandable>⚖️<u>𝗞𝗔𝗥𝗠𝗔 𝗠𝗔𝗦𝗦 𝗥𝗘𝗣𝗢𝗥𝗧𝗘𝗥</u>⚖️</blockquote>
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
        photo="https://imghosting.in/host/z8lk74",  
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


SETUP_GUIDE_TEXT = """
<blockquote expandable>📘 <u>𝗨𝗦𝗔𝗚𝗘 𝗚𝗨𝗜𝗗𝗘</u> :</blockquote>

<blockquote>1️⃣ 𝗔𝗗𝗗 𝗔𝗖𝗖𝗢𝗨𝗡𝗧𝗦
<b>➤ Add multiple active accounts to ensure better coverage and efficiency.</b></blockquote>
<blockquote>2️⃣ 𝗣𝗥𝗘𝗣𝗔𝗥𝗘 𝗘𝗡𝗩𝗜𝗥𝗢𝗡𝗠𝗘𝗡𝗧  
<b>➤ Create at least 6-7 public groups from all your IDs. </b></blockquote>
<blockquote>3️⃣ 𝗦𝗘𝗟𝗘𝗖𝗧 𝗧𝗔𝗥𝗚𝗘𝗧
<b>➤ Choose the content or profile that requires reporting.</b></blockquote>
<blockquote>4️⃣ 𝗖𝗛𝗢𝗢𝗦𝗘 𝗥𝗘𝗔𝗦𝗢𝗡
<b>➤ Select an appropriate and valid reason for the report.</b></blockquote>
<blockquote>5️⃣ 𝗦𝗧𝗔𝗥𝗧 𝗣𝗥𝗢𝗖𝗘𝗦𝗦  
<b>➤ Initiate reporting and monitor progress from the dashboard.</b></blockquote>

<b><i>🚀 Stay safe and use wisely.</i></b>
"""

async def cb_setup_guide(client: Client, callback: CallbackQuery):
    await callback.message.edit_text(
        SETUP_GUIDE_TEXT,
        parse_mode=ParseMode.HTML,
        reply_markup=kb_setup_guide()
    )

async def cb_back_to_start(client: Client, callback: CallbackQuery):
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media="https://imghosting.in/host/z8lk74",  # image URL ya file path
            caption=WELCOME_TEXT
        ),
        reply_markup=kb_start()
    )


def kb_setup_guide():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞", callback_data="back_to_start")],
    ])
