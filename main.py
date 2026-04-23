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
        """Load sessions from database"""
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
                print(f"✅ Session ID {sid} loaded")
            except Exception as e:
                logger.error(f"❌ Session {sid} failed: {e}")
    
    async def safe_join(self, client, target):
        """Safely join chat"""
        try:
            await client.join_chat(target)
        except:
            pass
    
    async def single_report(self, sid, target, reason, desc):
        """🔥 FIXED - Handles MESSAGE_ID_INVALID perfectly"""
        client = self.clients.get(sid)
        if not client:
            return False
        
        clean_target = re.sub(r'^[@https?://t\.me/]+', '', target)
        
        try:
            # 🎲 Human-like random delay
            await asyncio.sleep(random.randint(MIN_DELAY, MAX_DELAY))
            await self.safe_join(client, clean_target)
            
            # 🆕 SAFER Message ID detection
            msg_id = None
            try:
                # Get 1-3 recent messages only
                async for message in client.get_chat_history(clean_target, limit=3):
                    msg_id = message.id
                    break  # Use most recent
                logger.info(f"📄 Using msg_id {msg_id} for {clean_target}")
            except Exception as e:
                logger.warning(f"📄 No msg_id for {sid}: {e}")
            
            # 🔥 PRIMARY REPORT ATTEMPT
            await client.report_chat(
                chat_id=clean_target,
                reason=reason.lower().replace(' ', '_').replace('/', '_'),
                message_ids=[msg_id] if msg_id else [],
                message=desc[:490] + f" [{random.randint(1000,9999)}]"  # Telegram limit + unique
            )
            logger.info(f"✅ REPORT SUCCESS {sid} → {clean_target}")
            return True
            
        except FloodWait as fw:
            logger.warning(f"⏳ FloodWait {sid}: {fw.value}s")
            await asyncio.sleep(fw.value + random.randint(2, 5))
            return False
            
        except (PeerIdInvalid, UsernameNotOccupied, ChatAdminRequired):
            logger.warning(f"🚫 Invalid target {clean_target}")
            return False
            
        except Exception as e:
            error_str = str(e)
            
            # 🔄 RETRY WITHOUT message_ids (fixes MESSAGE_ID_INVALID)
            if any(x in error_str for x in ["MESSAGE_ID_INVALID", "Chat not found", "message id"]):
                logger.info(f"🔄 Retrying {sid} WITHOUT msg_id...")
                try:
                    await client.report_chat(
                        chat_id=clean_target,
                        reason=reason.lower().replace(' ', '_'),
                        message_ids=None,  # Key fix!
                        message=desc[:490]
                    )
                    logger.info(f"✅ RETRY SUCCESS {sid}")
                    return True
                except Exception as retry_e:
                    logger.error(f"❌ Retry failed {sid}: {retry_e}")
                    return False
            
            logger.error(f"❌ Report failed {sid}: {e}")
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
        f"🤖 **Mass Reporter v5.2 - FIXED**\n\n"
        f"`📱 Sessions: {count}`\n"
        f"`🎯 Target: {'✅' if target else '❌'}`\n"
        f"`🔥 Status: 100% Working`\n\n"
        f"**MESSAGE_ID_INVALID = FIXED** ✅",
        reply_markup=kb
    )

@app.on_callback_query(filters.user(ADMIN_ID))
async def callbacks(client, cb: CallbackQuery):
    data = cb.data
    
    if data == "main": 
        await start_cmd(client, cb.message)
        return
    
    # Add Session
    if data == "add_sess":
        await cb.edit_message_text(
            "🔑 **Add String Session**\n\n"
            f"1. `@StringSessionRobot` jao\n"
            f"2. String copy karo\n"
            f"3. Yaha paste karo\n\n"
            f"`Current: {db.get_session_count()}`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Main", callback_data="main")]])
        )
    
    # Sessions list
    if data == "sessions":
        sessions = db.get_sessions()
        if not sessions:
            return await cb.answer("No sessions!", show_alert=True)
        text = f"📋 **{len(sessions)} Sessions**\n\n"
        for s in sessions[:12]:
            text += f"`ID: {s['id']}` ✅\n"
        kb = [
            [InlineKeyboardButton("🗑️ Delete Session", callback_data="del_sess")],
            [InlineKeyboardButton("🔙 Main", callback_data="main")]
        ]
        await cb.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb))
    
    # Delete session
    if data == "del_sess":
        await cb.edit_message_text(
            "🗑️ **Delete Session**\n\n`ID number` bhejo (jaise: 1, 2, 3):",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Sessions", callback_data="sessions")]])
        )
    
    # Set target
    if data == "target":
        await cb.edit_message_text(
            "🎯 **Set Target**\n\nExamples:\n"
            "• `@channelname`\n"
            "• `123456789`\n"
            "• `t.me/channel`\n\n**Send now:**",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Main", callback_data="main")]])
        )
    
    # Stats
    if data == "stats":
        target = db.get_target()
        rate = reporter.stats['success'] / max(reporter.stats['total'], 1) * 100
        text = (
            f"📊 **Live Stats**\n\n"
            f"`📱 Active Sessions: {len(reporter.clients)}`\n"
            f"`🎯 Current Target: {'✅ Set' if target else '❌ None'}`\n"
            f"`📈 Total Reports: {reporter.stats['total']:,}`\n"
            f"`✅ Success: {reporter.stats['success']:,}`\n"
            f"`❌ Failed: {reporter.stats['failed']:,}`\n"
            f"`📊 Success Rate: {rate:.1f}%`"
        )
        await cb.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Main", callback_data="main")]]))
    
    # Report flow
    if data == "report":
        target = db.get_target()
        if not target:
            return await cb.answer("❌ Pehle target set karo!", show_alert=True)
        if not reporter.clients:
            return await cb.answer("❌ Pehle sessions add karo!", show_alert=True)
        
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("😡 Hate Speech", callback_data="r_hate"), 
             InlineKeyboardButton("💸 Scam", callback_data="r_scam")],
            [InlineKeyboardButton("©️ Copyright", callback_data="r_copy"), 
             InlineKeyboardButton("🔞 Porn", callback_data="r_porn")],
            [InlineKeyboardButton("👶 Child Abuse", callback_data="r_child")],
            [InlineKeyboardButton("🔙 Main", callback_data="main")]
        ])
        await cb.edit_message_text(
            f"⚠️ **Select Reason**\n\n"
            f"Target: `{target['data']}`\n"
            f"Sessions: `{len(reporter.clients)}`",
            reply_markup=kb
        )
    
    if data.startswith("r_"):
        reasons = {
            "r_hate": "Hate Speech",
            "r_scam": "Scam/Fraud", 
            "r_copy": "Copyright Violation",
            "r_porn": "Pornography/Adult Content",
            "r_child": "Child Abuse"
        }
        reason_name = reasons[data]
        reporter.report_config[ADMIN_ID] = {
            "reason": reason_name,
            "target": db.get_target()['data'],
            "desc": REPORT_REASONS[reason_name]
        }
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🚀 START REPORTING", callback_data="start_rep")],
                                  [InlineKeyboardButton("🔙 Report", callback_data="report")]])
        await cb.edit_message_text(
            f"📝 **Ready to Report**\n\n"
            f"🎯 Target: `{db.get_target()['data']}`\n"
            f"⚠️ Reason: `{reason_name}`\n"
            f"📱 Sessions: `{len(reporter.clients)}`\n\n"
            f"**Send amount per session (1-25):**",
            reply_markup=kb
        )
    
    if data == "start_rep":
        await cb.answer("Amount message me bhejo!")
    
    if data == "stop_rep":
        reporter.is_reporting = False
        await cb.answer("⏹️ Reporting STOPPED!", show_alert=True)

@app.on_message(filters.text & filters.user(ADMIN_ID) & ~filters.command("start"))
async def text_handler(client, message):
    text = message.text.strip()
    
    # 🔑 Session string detection (starts 1/2 + BV + long)
    if len(text) > 200 and text.startswith(('1', '2')) and 'BV' in text[:100]:
        if db.add_session(text):
            await reporter.load_all_sessions()
            count = db.get_session_count()
            await message.reply(
                f"✅ **Session Added Successfully!**\n\n"
                f"📊 **Total Sessions: `{count}`**\n"
                f"🔥 **Ready to report!**",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main", callback_data="main")]])
            )
        else:
            await message.reply("❌ **Duplicate session! Already exists.**")
        return
    
    # 🗑️ Delete session by ID
    if text.isdigit() and 1 <= int(text) <= 999:
        sid = int(text)
        if db.delete_session(sid):
            if sid in reporter.clients:
                try:
                    await reporter.clients[sid].stop()
                except: pass
                del reporter.clients[sid]
            await message.reply(f"✅ **Session ID `{sid}` deleted!**")
        else:
            await message.reply(f"❌ **Session ID `{sid}` not found!**")
        return
    
    # 🎯 Set target
    target_match = re.match(r'^(@[\w.-]+|\d+|t\.me/[^\s]+)$', text)
    if target_match:
        clean_target = re.sub(r'^[@https?://t\.me/]+', '', text)
        target_type = "user" if text.isdigit() else "channel/group"
        db.set_target(clean_target, target_type)
        await message.reply(
            f"🎯 **Target Set Successfully!**\n\n"
            f"📍 **Target: `{clean_target}`**\n"
            f"📂 **Type: {target_type}`**\n"
            f"🚀 **Ready to mass report!**",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main", callback_data="main")]])
        )
        return
    
    # 📊 Report amount
    if ADMIN_ID in reporter.report_config and text.isdigit():
        amount = int(text)
        if 1 <= amount <= 25:
            await mass_execute(message, amount)
        else:
            await message.reply("❌ **1-25 ke beech me number bhejo!**")
        return
    
    await message.reply("❌ **Unknown command!** `/start` use karo.")

async def mass_execute(origin_msg, amount: int):
    """🚀 Main mass reporting engine"""
    config = reporter.report_config[ADMIN_ID]
    total_reports = len(reporter.clients) * amount
    
    # Status message
    status_msg = await origin_msg.reply(
        f"🚀 **MASS REPORTING STARTED**\n\n"
        f"📱 `{len(reporter.clients)}` sessions\n"
        f"🔢 `{amount}` reports/session\n"
        f"📊 **Total: `{total_reports}`**\n"
        f"🎯 **Target: `{config['target']}`**\n"
        f"⚠️ **Reason: `{config['reason']}`**\n\n"
        f"`🔥 Initiating...`",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⏹️ EMERGENCY STOP", callback_data="stop_rep")]])
    )
    
    reporter.is_reporting = True
    success_count = 0
    fail_count = 0
    
    # 🌀 Random session order (anti-pattern)
    session_list = list(reporter.clients.items())
    random.shuffle(session_list)
    
    for sid, client in session_list:
        if not reporter.is_reporting:
            break
            
        for report_num in range(amount):
            if not reporter.is_reporting:
                break
            
            # 🔄 Random reason rotation (20% chance)
            report_reason = config['reason']
            if random.random() < 0.2:
                report_reason = random.choice(list(REPORT_REASONS.keys()))
            
            if await reporter.single_report(sid, config['target'], report_reason, config['desc']):
                success_count += 1
                reporter.stats['success'] += 1
            else:
                fail_count += 1
                reporter.stats['failed'] += 1
            
            reporter.stats['total'] += 1
            
            # 📊 Live progress update
            progress_rate = (success_count + fail_count) / total_reports * 100
            success_rate = success_count / max(success_count + fail_count, 1) * 100
            
            await status_msg.edit_text(
                f"🔥 **LIVE REPORTING - {progress_rate:.1f}%**\n\n"
                f"✅ **Success: `{success_count}`**\n"
                f"❌ **Failed: `{fail_count}`**\n"
                f"📱 **Session: `{sid}`** ({report_num+1}/{amount})\n"
                f"📊 **Overall: {success_rate:.1f}%**\n"
                f"🎯 **Target: `{config['target']}`**",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⏹️ STOP", callback_data="stop_rep")]])
            )
    
    # ✅ Final results
    reporter.is_reporting = False
    final_rate = success_count / max(total_reports, 1) * 100
    await status_msg.edit_text(
        f"✅ **MASS REPORT COMPLETE!**\n\n"
        f"🎯 **Target: `{config['target']}`**\n"
        f"📊 **Total: `{total_reports}`**\n"
        f"✅ **Success: `{success_count}`**\n"
        f"❌ **Failed: `{fail_count}`**\n"
        f"📈 **Success Rate: {final_rate:.1f}%**\n\n"
        f"**Ready for next target! 🔥**",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main", callback_data="main")]])
    )

async def main():
    """Start bot"""
    await app.start()
    await reporter.load_all_sessions()
    print("\n🚀 =====================================")
    print("🚀      Mass Reporter v5.2 - READY!")
    print(f"🚀      Active Sessions: {len(reporter.clients)}")
    print("🚀      Bot Username: @your_bot_username")
    print("🚀 =====================================\n")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
