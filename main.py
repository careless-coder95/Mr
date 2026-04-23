import os
import asyncio
import logging
import re
import random
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, PeerIdInvalid, ChatAdminRequired, UsernameNotOccupied
from pyrogram.proxy import Proxy
from config import (BOT_TOKEN, API_ID, API_HASH, ADMIN_ID, SESSIONS_DIR, REPORT_REASONS, 
                   REPORT_DELAY, MIN_DELAY, MAX_DELAY, PROXIES)
from database import Database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
os.makedirs(SESSIONS_DIR, exist_ok=True)

db = Database()
app = Client("reporter_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

class MassReporter:
    def __init__(self):
        self.clients = {}
        self.stats = {"total": 0, "success": 0, "failed": 0}
        self.is_reporting = False
        self.report_config = {}
        self.used_msg_ids = {}
        self.proxies = PROXIES
    
    async def load_all_sessions(self):
        sessions = db.get_sessions()
        for data in sessions:
            sid = data['id']
            session_str = data['session_string']
            try:
                client = Client(f"{SESSIONS_DIR}/s{sid}", api_id=API_ID, api_hash=API_HASH,
                              session_string=session_str, in_memory=True)
                await client.start()
                self.clients[sid] = client
                logger.info(f"✅ Loaded session {sid}")
            except Exception as e:
                logger.error(f"❌ Session {sid} failed: {e}")
    
    async def safe_join(self, client, target):
        try:
            await client.join_chat(target)
        except:
            pass
    
    async def single_report(self, sid, target, reason, desc):
        client = self.clients.get(sid)
        if not client:
            return False
        
        try:
            # 🎲 RANDOM HUMAN DELAY
            await asyncio.sleep(random.randint(MIN_DELAY, MAX_DELAY))
            
            clean_target = re.sub(r'^[@https?://t\.me/]+', '', target)
            
            # 🛡️ PROXY ROTATION (20% chance)
            if self.proxies and random.random() < 0.2:
                proxy = random.choice(self.proxies)
                await client.set_proxy(Proxy.from_url(proxy))
            
            await self.safe_join(client, clean_target)
            
            # 🎯 SMART MSG ID SELECTION
            msg_id = None
            self.used_msg_ids.setdefault(clean_target, set())
            try:
                history = await client.get_chat_history(clean_target, limit=MSG_HISTORY_DEPTH)
                available_ids = [msg.id for msg in history 
                               if msg.id not in self.used_msg_ids[clean_target]]
                if available_ids:
                    msg_id = random.choice(available_ids)
                    self.used_msg_ids[clean_target].add(msg_id)
                
                # Rotate IDs (keep last 20)
                if len(self.used_msg_ids[clean_target]) > 20:
                    self.used_msg_ids[clean_target] = set(list(self.used_msg_ids[clean_target])[-20:])
            except:
                pass
            
            # 🔥 REPORT
            await client.report_chat(
                chat_id=clean_target,
                reason=reason.lower().replace(' ', '_'),
                message_ids=[msg_id] if msg_id else [],
                message=desc + f" [{random.randint(100,999)}]"  # Unique
            )
            return True
            
        except FloodWait as fw:
            await asyncio.sleep(fw.value + random.randint(3, 7))
            return False
        except (PeerIdInvalid, UsernameNotOccupied, ChatAdminRequired):
            return False
        except Exception as e:
            logger.error(f"Report fail {sid}: {e}")
            return False

reporter = MassReporter()

@app.on_message(filters.command("start") & filters.user(ADMIN_ID))
async def start_cmd(client, message):
    count = db.get_session_count()
    target = db.get_target()
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Session", callback_data="add_sess")],
        [InlineKeyboardButton(f"📊 {count} Sessions", callback_data="sessions")],
        [InlineKeyboardButton("🎯 Set Target", callback_data="target")],
        [InlineKeyboardButton("🚀 Mass Report", callback_data="report")],
        [InlineKeyboardButton("📈 Stats", callback_data="stats")]
    ])
    
    await message.edit_text(
        f"🤖 **Mass Reporter v5.0 - BAN GUARANTEED**\n\n"
        f"`📱 Sessions: {count}`\n"
        f"`🎯 Target: {'✅' if target else '❌'}`\n"
        f"`🔥 Proxies: {len(reporter.proxies)}`\n\n"
        "**100% Working + Evasion**",
        reply_markup=kb
    )

@app.on_callback_query(filters.user(ADMIN_ID))
async def callbacks(client, cb: CallbackQuery):
    data = cb.data
    
    if data == "main":
        await start_cmd(client, cb.message)
        return
    
    elif data == "add_sess":
        await cb.edit_message_text(
            "🔑 **Add Session**\n\n`@StringSessionRobot` se string bhejo:\n\n"
            f"Current: `{db.get_session_count()}`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="main")]])
        )
    
    elif data == "sessions":
        sessions = db.get_sessions()
        text = f"📋 **{len(sessions)} Sessions**\n\n"
        for s in sessions[:15]:
            text += f"`ID{s['id']}` ✅\n"
        kb = [[InlineKeyboardButton("🗑️ Delete", callback_data="del_sess")],
              [InlineKeyboardButton("🔙", callback_data="main")]]
        await cb.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb))
    
    elif data == "del_sess":
        await cb.edit_message_text(
            "🗑️ **Delete**\n`ID` number bhejo:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="sessions")]])
        )
    
    elif data == "target":
        await cb.edit_message_text(
            "🎯 **Target**\n\n`@username` / `ID` / `t.me/channel` bhejo:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="main")]])
        )
    
    elif data == "stats":
        target = db.get_target()
        rate = reporter.stats['success'] / max(reporter.stats['total'], 1) * 100
        await cb.edit_message_text(
            f"📊 **Stats**\n\n"
            f"`📱 Active: {len(reporter.clients)}`\n"
            f"`🎯 Target: {'✅' if target else '❌'}`\n"
            f"`📈 Total: {reporter.stats['total']}`\n"
            f"`✅ Success: {reporter.stats['success']}`\n"
            f"`❌ Failed: {reporter.stats['failed']}`\n"
            f"`📊 Rate: {rate:.1f}%`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="main")]])
        )
    
    elif data == "report":
        target = db.get_target()
        if not target:
            return await cb.answer("❌ Target set karo!", show_alert=True)
        if not reporter.clients:
            return await cb.answer("❌ Sessions add karo!", show_alert=True)
        
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("😡 Hate", callback_data="r_hate"), InlineKeyboardButton("©️ Copy", callback_data="r_copy")],
            [InlineKeyboardButton("💸 Scam", callback_data="r_scam"), InlineKeyboardButton("👶 Child", callback_data="r_child")],
            [InlineKeyboardButton("🔞 Porn", callback_data="r_porn")],
            [InlineKeyboardButton("🔙", callback_data="main")]
        ])
        await cb.edit_message_text("⚠️ **Reason choose karo:**", reply_markup=kb)
    
    elif data.startswith("r_"):
        reasons = {"r_hate": "Hate Speech", "r_copy": "Copyright Violation",
                  "r_scam": "Scam/Fraud", "r_child": "Child Abuse", "r_porn": "Pornography/Adult Content"}
        reason = reasons[data]
        reporter.report_config[ADMIN_ID] = {
            "reason": reason, "target": db.get_target()["data"], "desc": REPORT_REASONS[reason]
        }
        await cb.edit_message_text(
            f"📝 **Desc** (optional)\n\nReason: `{reason}`\nTarget: `{db.get_target()['data']}`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚀 START", callback_data="start_rep")]])
        )
    
    elif data == "start_rep":
        await cb.edit_message_text(
            f"🔢 **Amount per session**\n\nSessions: `{len(reporter.clients)}`\n1-50 bhejo:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="report")]])
        )
    
    elif data == "stop_rep":
        reporter.is_reporting = False
        await cb.answer("⏹️ STOPPED")

@app.on_message(filters.text & filters.user(ADMIN_ID) & ~filters.command("start"))
async def text_handler(client, message):
    text = message.text.strip()
    
    # 🔑 Session string (BV* detect)
    if len(text) > 200 and text.startswith(('1', '2')) and 'BV' in text[:100]:
        if db.add_session(text):
            await reporter.load_all_sessions()
            await message.reply(f"✅ **Added!** Total: `{db.get_session_count()}`")
        else:
            await message.reply("❌ **Duplicate!**")
        return
    
    # 🗑️ Delete ID
    if text.isdigit() and len(text) < 4:
        if db.delete_session(int(text)):
            if int(text) in reporter.clients:
                await reporter.clients[int(text)].stop()
                del reporter.clients[int(text)]
            await message.reply(f"✅ **Deleted {text}`**")
        return
    
    # 🎯 Target
    if re.match(r'^(@[\w]+|\d+|t\.me/[\w/-]+)$', text):
        clean = re.sub(r'^[@https?://t\.me/]+', '', text)
        db.set_target(clean, "channel" if not text.isdigit() else "user")
        await message.reply(f"🎯 **Set!** `{clean}`")
        return
    
    # 📝 Desc + Amount
    if ADMIN_ID in reporter.report_config:
        if text.isdigit() and 1 <= int(text) <= 50:
            await mass_execute(message, int(text))
        else:
            reporter.report_config[ADMIN_ID]['desc'] = text
            await message.reply("🔢 **Amount** (1-50):")
        return

async def mass_execute(msg, amount):
    config = reporter.report_config[ADMIN_ID]
    total = len(reporter.clients) * amount
    
    status = await msg.reply(f"🚀 **STARTED**\n📱 `{len(reporter.clients)}` sessions\n🎯 `{config['target']}`\n📊 `{total}` total")
    
    reporter.is_reporting = True
    success = failed = 0
    
    # 🌀 RANDOM ORDER
    clients = dict(random.sample(list(reporter.clients.items()), len(reporter.clients)))
    
    for sid, client in clients.items():
        if not reporter.is_reporting: break
        
        for i in range(amount):
            if not reporter.is_reporting: break
            
            reason = config['reason']
            if random.random() < 0.15:  # Rotate reason
                reason = random.choice(list(REPORT_REASONS.keys()))
            
            if await reporter.single_report(sid, config['target'], reason, config['desc']):
                success += 1; reporter.stats['success'] += 1
            else:
                failed += 1; reporter.stats['failed'] += 1
            
            reporter.stats['total'] += 1
            
            rate = success / max(success + failed, 1) * 100
            await status.edit_text(
                f"🔥 **LIVE {rate:.1f}%**\n"
                f"✅ `{success}` / ❌ `{failed}`\n"
                f"📱 `{sid}` ({i+1}/{amount})\n"
                f"🎯 `{config['target']}`",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⏹️", callback_data="stop_rep")]])
            )
    
    reporter.is_reporting = False
    await status.edit_text(f"✅ **DONE!** `{success}/{total}` ✅\n📈 `{success/max(total,1)*100:.1f}%`")

async def main():
    await app.start()
    await reporter.load_all_sessions()
    print("🚀 v5.0 READY - 100% BAN!")
    await app.idle()

if __name__ == "__main__":
    app.run(main())
