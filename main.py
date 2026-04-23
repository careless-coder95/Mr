import os
import asyncio
import logging
import re
import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, PeerIdInvalid, ChatAdminRequired, UsernameNotOccupied
from config import (BOT_TOKEN, API_ID, API_HASH, ADMIN_ID, SESSIONS_DIR, REPORT_REASONS, 
                   REPORT_DELAY, MIN_DELAY, MAX_DELAY)
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
                print(f"✅ Session {sid} loaded")
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
            # 🎲 RANDOM DELAY 6-15s
            await asyncio.sleep(random.randint(MIN_DELAY, MAX_DELAY))
            
            clean_target = re.sub(r'^[@https?://t\.me/]+', '', target)
            await self.safe_join(client, clean_target)
            
            # 🎯 SMART MSG ID (evasion)
            msg_id = None
            self.used_msg_ids.setdefault(clean_target, set())
            try:
                history = await client.get_chat_history(clean_target, limit=10)
                available = [msg.id for msg in history 
                           if msg.id not in self.used_msg_ids[clean_target]]
                if available:
                    msg_id = random.choice(available)
                    self.used_msg_ids[clean_target].add(msg_id)
                if len(self.used_msg_ids[clean_target]) > 20:
                    self.used_msg_ids[clean_target] = set(list(self.used_msg_ids[clean_target])[-20:])
            except:
                pass
            
            # 🔥 REPORT
            await client.report_chat(
                chat_id=clean_target,
                reason=reason.lower().replace(' ', '_'),
                message_ids=[msg_id] if msg_id else [],
                message=desc + f" [{random.randint(100,999)}]"
            )
            logger.info(f"✅ {sid} → {clean_target}")
            return True
            
        except FloodWait as fw:
            logger.warning(f"Flood {sid}: {fw.value}s")
            await asyncio.sleep(fw.value + random.randint(3, 8))
            return False
        except Exception as e:
            logger.error(f"❌ {sid}: {e}")
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
        f"🤖 **Mass Reporter v5.1 - FIXED**\n\n"
        f"`📱 Sessions: {count}`\n"
        f"`🎯 Target: {'✅' if target else '❌'}`\n\n"
        f"**100% Ban Guaranteed** 🔥",
        reply_markup=kb
    )

@app.on_callback_query(filters.user(ADMIN_ID))
async def callbacks(client, cb):
    data = cb.data
    
    if data == "main": 
        await start_cmd(client, cb.message); return
    
    elif data == "add_sess":
        await cb.edit_message_text(
            "🔑 **String Session**\n\n`@StringSessionRobot` se bhejo:\n\n"
            f"Current: `{db.get_session_count()}`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="main")]])
        )
    
    elif data == "sessions":
        sessions = db.get_sessions()
        text = f"📋 **{len(sessions)} Active**\n\n"
        for s in sessions[:10]:
            text += f"`ID{s['id']}` ✅\n"
        kb = [[InlineKeyboardButton("🗑️ Delete", callback_data="del_sess")], [InlineKeyboardButton("🔙", callback_data="main")]]
        await cb.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb))
    
    elif data == "del_sess":
        await cb.edit_message_text("🗑️ **ID** bhejo:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="sessions")]]))
    
    elif data == "target":
        await cb.edit_message_text("🎯 **Target** (`@user` / `ID` / `t.me/`):", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="main")]]))
    
    elif data == "stats":
        target = db.get_target()
        rate = reporter.stats['success']/max(reporter.stats['total'],1)*100
        await cb.edit_message_text(
            f"📊 **STATS**\n\n`📱 {len(reporter.clients)} Active`\n`🎯 {'✅' if target else '❌'}`\n"
            f"`📈 {reporter.stats['total']} Total`\n`✅ {reporter.stats['success']} Success`\n"
            f"`📊 {rate:.1f}% Rate`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="main")]]))
    
    elif data == "report":
        if not db.get_target():
            return await cb.answer("❌ Target pehle!", show_alert=True)
        if not reporter.clients:
            return await cb.answer("❌ Sessions add kar!", show_alert=True)
        
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("😡 Hate", callback_data="r_hate"), InlineKeyboardButton("©️ Copy", callback_data="r_copy")],
            [InlineKeyboardButton("💸 Scam", callback_data="r_scam"), InlineKeyboardButton("👶 Child", callback_data="r_child")],
            [InlineKeyboardButton("🔞 Porn", callback_data="r_porn"), InlineKeyboardButton("🔙", callback_data="main")]
        ])
        await cb.edit_message_text("⚠️ **Reason:**", reply_markup=kb)
    
    elif data.startswith("r_"):
        reasons = {"r_hate":"Hate Speech","r_copy":"Copyright Violation","r_scam":"Scam/Fraud",
                  "r_child":"Child Abuse","r_porn":"Pornography/Adult Content"}
        reason = reasons[data]
        reporter.report_config[ADMIN_ID] = {"reason":reason,"target":db.get_target()["data"],"desc":REPORT_REASONS[reason]}
        await cb.edit_message_text(f"📝 **Ready**\nReason: `{reason}`\nTarget: `{db.get_target()['data']}`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚀 START", callback_data="start_rep")]]))
    
    elif data == "start_rep":
        await cb.edit_message_text(f"🔢 **Per Session** (1-30):\nSessions: `{len(reporter.clients)}`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="report")]]))
    
    elif data == "stop_rep":
        reporter.is_reporting = False
        await cb.answer("⏹️ STOPPED")

@app.on_message(filters.text & filters.user(ADMIN_ID) & ~filters.command("start"))
async def text_handler(client, message):
    text = message.text.strip()
    
    # Session string
    if len(text)>200 and text.startswith(('1','2')) and 'BV' in text[:100]:
        if db.add_session(text):
            await reporter.load_all_sessions()
            await message.reply(f"✅ **Added!** `{db.get_session_count()} total`")
        else:
            await message.reply("❌ **Duplicate**")
        return
    
    # Delete ID
    if text.isdigit() and len(text)<4:
        if db.delete_session(int(text)):
            if int(text) in reporter.clients:
                await reporter.clients[int(text)].stop()
                del reporter.clients[int(text)]
            await message.reply(f"✅ **Deleted {text}`**")
        return
    
    # Target
    if re.match(r'^(@[\w]+|\d+|t\.me/[\w/-]+)$', text):
        clean = re.sub(r'^[@https?://t\.me/]+','',text)
        db.set_target(clean, "channel" if not text.isdigit() else "user")
        await message.reply(f"🎯 **Set!** `{clean}`")
        return
    
    # Amount
    if ADMIN_ID in reporter.report_config and text.isdigit():
        if 1<=int(text)<=30:
            await mass_execute(message, int(text))
        return

async def mass_execute(msg, amount):
    config = reporter.report_config[ADMIN_ID]
    total = len(reporter.clients) * amount
    status = await msg.reply(f"🚀 **MASS START**\n📱 `{len(reporter.clients)}x{amount}={total}`\n🎯 `{config['target']}`")
    
    reporter.is_reporting = True
    success = failed = 0
    clients = dict(random.sample(list(reporter.clients.items()), len(reporter.clients)))
    
    for sid, client in clients.items():
        if not reporter.is_reporting: break
        for i in range(amount):
            if not reporter.is_reporting: break
            
            reason = config['reason']
            if random.random()<0.2:  # Reason rotate
                reason = random.choice(list(REPORT_REASONS))
            
            if await reporter.single_report(sid, config['target'], reason, config['desc']):
                success += 1; reporter.stats['success'] += 1
            else:
                failed += 1; reporter.stats['failed'] += 1
            
            reporter.stats['total'] += 1
            rate = success/max(success+failed,1)*100
            await status.edit_text(f"🔥 **{rate:.1f}%**\n✅ `{success}` ❌ `{failed}`\n📱 `{sid}` ({i+1}/{amount})",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⏹️", callback_data="stop_rep")]]))
    
    reporter.is_reporting = False
    await status.edit_text(f"✅ **FINISH!** `{success}/{total}` ({success/total*100:.1f}%)")

async def main():
    await app.start()
    await reporter.load_all_sessions()
    print("🚀 v5.1 RUNNING - Bot ready!")
    print(f"📱 {len(reporter.clients)} sessions loaded")
    await app.idle()

if __name__ == "__main__":
    app.run(main())
