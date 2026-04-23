import os
import asyncio
import logging
import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, PeerIdInvalid, ChatAdminRequired, UsernameNotOccupied
from config import BOT_TOKEN, ADMIN_ID, SESSIONS_DIR, REPORT_REASONS, REPORT_DELAY
from database import Database

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
os.makedirs(SESSIONS_DIR, exist_ok=True)

# Globals
db = Database()
app = Client("reporter_bot", bot_token=BOT_TOKEN)

class MassReporter:
    def __init__(self):
        self.clients = {}
        self.stats = {"total": 0, "success": 0, "failed": 0}
        self.state = {}  # user_state tracking
        self.is_reporting = False
        
    async def load_all_sessions(self):
        """Load all sessions from DB"""
        sessions = db.get_sessions()
        for data in sessions:
            sid = data['id']
            session_str = data['session_string']
            try:
                client = Client(f"{SESSIONS_DIR}/s{sid}", session_string=session_str, in_memory=True)
                await client.start()
                self.clients[sid] = client
                logger.info(f"Loaded session {sid}")
            except Exception as e:
                logger.error(f"Session {sid} failed: {e}")
    
    async def safe_join(self, client, target):
        """Safely join target if needed"""
        try:
            await client.join_chat(target)
        except:
            pass
    
    async def single_report(self, sid, target, reason, desc):
        """Single report attempt"""
        client = self.clients.get(sid)
        if not client:
            return False
        
        try:
            clean_target = re.sub(r'^[@https?://t\.me/]+', '', target)
            
            # Join if channel/group
            await self.safe_join(client, clean_target)
            
            # Get recent message for channels
            msg_id = None
            try:
                async for msg in client.get_chat_history(clean_target, limit=1):
                    msg_id = msg.id
                    break
            except:
                pass
            
            # Report!
            await client.report_chat(
                chat_id=clean_target,
                reason=reason.lower().replace(' ', '_').replace('/', '_'),
                message_ids=[msg_id] if msg_id else [],
                message=desc
            )
            return True
            
        except FloodWait as fw:
            await asyncio.sleep(fw.value)
            return False
        except (PeerIdInvalid, UsernameNotOccupied, ChatAdminRequired):
            return False
        except Exception as e:
            logger.error(f"Report error {sid}: {e}")
            return False

reporter = MassReporter()

# ================= COMMANDS =================
@app.on_message(filters.command("start") & filters.user(ADMIN_ID))
async def start_cmd(client, message):
    count = db.get_session_count()
    target = db.get_target()
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Session", callback_data="add_sess")],
        [InlineKeyboardButton(f"📊 Sessions: {count}", callback_data="sessions")],
        [InlineKeyboardButton("🎯 Set Target", callback_data="target")],
        [InlineKeyboardButton("🚀 Mass Report", callback_data="report")],
        [InlineKeyboardButton("📈 Stats", callback_data="stats")]
    ])
    
    await message.edit_text(
        f"🤖 **Mass Reporter v3.0**\n\n"
        f"`📱 Sessions: {count}`\n"
        f"`🎯 Target: {'✅' if target else '❌'}`\n\n"
        "👇 Select:",
        reply_markup=kb
    )

# ================= CALLBACKS =================
@app.on_callback_query(filters.user(ADMIN_ID))
async def callbacks(client, cb: CallbackQuery):
    data = cb.data
    
    # Navigation
    if data == "main":
        await start_cmd(client, cb.message)
    
    # Sessions
    elif data == "add_sess":
        await cb.edit_message_text(
            "🔑 **Add Session**\n\nSend string session:\n`@StringSessionRobot`\n\n"
            f"Current: `{db.get_session_count()}`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="main")]])
        )
    
    elif data == "sessions":
        sessions = db.get_sessions()
        if not sessions:
            return await cb.answer("No sessions", show_alert=True)
        
        text = f"📋 **Sessions: {len(sessions)}**\n\n"
        for s in sessions:
            text += f"`ID {s['id']}` ✅\n"
        
        kb = [[InlineKeyboardButton("🗑️ Delete", callback_data="del_sess")]]
        kb.append([InlineKeyboardButton("🔙", callback_data="main")])
        await cb.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb))
    
    elif data == "del_sess":
        await cb.edit_message_text(
            "🗑️ **Delete Session**\nSend `ID` number:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="sessions")]])
        )
    
    # Target
    elif data == "target":
        await cb.edit_message_text(
            "🎯 **Set Target**\n\nExamples:\n"
            "• `@username`\n"
            "• `123456`\n"
            "• `t.me/channel`\n\nSend now:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="main")]])
        )
    
    # Stats
    elif data == "stats":
        target = db.get_target()
        await cb.edit_message_text(
            f"📊 **Live Stats**\n\n"
            f"`📱 Sessions: {len(reporter.clients)}`\n"
            f"`🎯 Target: {'✅' if target else '❌'}`\n"
            f"`📈 Total: {reporter.stats['total']}`\n"
            f"`✅ Success: {reporter.stats['success']}`\n"
            f"`❌ Failed: {reporter.stats['failed']}`\n"
            f"`📊 Rate: {reporter.stats['success']/(reporter.stats['total'] or 1)*100:.1f}%`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="main")]])
        )
    
    # ================= REPORT FLOW =================
    elif data == "report":
        target = db.get_target()
        if not target:
            return await cb.answer("Set target first!", show_alert=True)
        if not reporter.clients:
            return await cb.answer("Add sessions first!", show_alert=True)
        
        # Reason selection
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("😡 Hate", callback_data="r_hate"), InlineKeyboardButton("©️ Copyright", callback_data="r_copy")],
            [InlineKeyboardButton("💸 Scam", callback_data="r_scam"), InlineKeyboardButton("👶 Child", callback_data="r_child")],
            [InlineKeyboardButton("🔞 Porn", callback_data="r_porn")],
            [InlineKeyboardButton("🔙", callback_data="main")]
        ])
        await cb.edit_message_text("⚠️ **Choose Reason:**", reply_markup=kb)
    
    elif data.startswith("r_"):
        reasons = {
            "r_hate": "Hate Speech",
            "r_copy": "Copyright Violation",
            "r_scam": "Scam/Fraud", 
            "r_child": "Child Abuse",
            "r_porn": "Pornography/Adult Content"
        }
        reporter.state[ADMIN_ID] = {"reason": reasons[data], "target": db.get_target()}
        await cb.edit_message_text(
            f"📝 **Description**\n\n"
            f"Reason: `{reasons[data]}`\n\n"
            f"Send description or use default:\n`{REPORT_REASONS[reasons[data]]}`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="report")]])
        )
    
    elif data == "start_mass":
        # Amount input handled in text handler
        pass

# ================= TEXT INPUTS =================
@app.on_message(filters.text & filters.user(ADMIN_ID) & ~filters.command("start"))
async def text_handler(client, message):
    text = message.text.strip()
    
    # Session string (long, starts 1/2)
    if len(text) > 100 and text[0] in '12':
        if db.add_session(text):
            await reporter.load_all_sessions()
            count = db.get_session_count()
            await message.reply(f"✅ **Added!** Total: `{count}`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠", callback_data="main")]]))
        else:
            await message.reply("❌ Duplicate!")
        return
    
    # Delete session ID
    if text.isdigit() and len(text) < 4:
        if db.delete_session(int(text)):
            if int(text) in reporter.clients:
                await reporter.clients[int(text)].stop()
                del reporter.clients[int(text)]
            await message.reply(f"✅ Deleted ID `{text}`")
        else:
            await message.reply("❌ Not found!")
        return
    
    # Target setting
    if re.match(r'^(@?\w+|t\.me/[\w/-]+|\d+)$', text):
        target_type = "user" if text.isdigit() else "channel"
        clean = re.sub(r'^[@https?://t\.me/]+', '', text)
        db.set_target(clean, target_type)
        await message.reply(f"🎯 **Target Set!**\nType: `{target_type}`\nID: `{clean}`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠", callback_data="main")]]))
        return
    
    # Report description
    if ADMIN_ID in reporter.state and 'reason' in reporter.state[ADMIN_ID]:
        reporter.state[ADMIN_ID]['desc'] = text or REPORT_REASONS[reporter.state[ADMIN_ID]['reason']]
        target = reporter.state[ADMIN_ID]['target']
        await message.reply(
            f"🔢 **Set Amount per Session**\n\n"
            f"Target: `{target['data']}`\n"
            f"Reason: `{reporter.state[ADMIN_ID]['reason']}`\n"
            f"Sessions: `{len(reporter.clients)}`\n\n"
            f"Send number (5-50):",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚀 START", callback_data="exec_report")]])
        )
        return
    
    # Amount input → EXECUTE!
    if ADMIN_ID in reporter.state and 'desc' in reporter.state[ADMIN_ID] and text.isdigit():
        amount = int(text)
        await mass_execute(message)
        return

# ================= MASS EXECUTION =================
async def mass_execute(origin_msg):
    """🚀 MAIN REPORTING ENGINE"""
    state = reporter.state[ADMIN_ID]
    target = state['target']['data']
    reason = state['reason']
    desc = state['desc']
    amount = int(origin_msg.text)
    
    total_sessions = len(reporter.clients)
    total_reports = total_sessions * amount
    
    status_msg = await origin_msg.reply(
        f"🚀 **Mass Report STARTED**\n\n"
        f"📱 `{total_sessions}` sessions\n"
        f"🔢 `{amount}` per session\n"
        f"🎯 Total: `{total_reports}`\n"
        f"⏳ `{target}`\n\n"
        "`🔥 Initiating...`",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⏹️ STOP", callback_data="stop_rep")]])
    )
    
    reporter.is_reporting = True
    success = 0
    failed = 0
    
    # Report loop
    for sid, client in list(reporter.clients.items()):
        if not reporter.is_reporting:
            break
            
        for _ in range(amount):
            if not reporter.is_reporting:
                break
                
            if await reporter.single_report(sid, target, reason, desc):
                success += 1
                reporter.stats['success'] += 1
            else:
                failed += 1
                reporter.stats['failed'] += 1
            
            reporter.stats['total'] += 1
            
            # Live update
            await status_msg.edit_text(
                f"🔥 **LIVE REPORTING**\n\n"
                f"📊 `{success}/{total_reports}` ✅\n"
                f"❌ `{failed}` failed\n"
                f"📱 Session `{sid}`\n"
                f"📈 `{success/(success+failed)*100:.1f}%`\n\n"
                f"⏳ `{REPORT_DELAY}s` cooldown"
            )
            await asyncio.sleep(REPORT_DELAY)
    
    # Complete
    reporter.is_reporting = False
    await status_msg.edit_text(
        f"✅ **COMPLETE!**\n\n"
        f"🎯 `{target}`\n"
        f"📊 `{success}/{total_reports}` ✅\n"
        f"❌ `{failed}` failed\n"
        f"📈 `{success/(success+failed)*100:.1f}%`\n\n"
        "Ready for next target!",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠", callback_data="main")]])
    )
    reporter.state.pop(ADMIN_ID, None)

@app.on_callback_query(filters.regex("stop_rep") & filters.user(ADMIN_ID))
async def stop_handler(client, cb):
    reporter.is_reporting = False
    await cb.answer("⏹️ STOPPED")

# ================= STARTUP =================
async def main():
    await reporter.load_all_sessions()
    logger.info(f"🤖 Started! {len(reporter.clients)} sessions active")
    await app.start()
    await app.idle()

if __name__ == "__main__":
    app.run(main())
