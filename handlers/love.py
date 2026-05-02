import asyncio
from pyrogram import Client
from pyrogram.types import Message, CallbackQuery
from utils.keyboards import kb_back_main, kb_main_menu
from utils.state import set_state, get_state, update_data, clear_state
from database.db import count_accounts
from pyrogram.enums import ParseMode

ORDINALS = [
    "First", "Second", "Third", "Fourth", "Fifth",
    "Sixth", "Seventh", "Eighth", "Ninth", "Tenth",
    "11th", "12th", "13th", "14th", "15th",
    "16th", "17th", "18th", "19th", "20th",
]

def get_ordinal(n: int) -> str:
    if n <= len(ORDINALS):
        return ORDINALS[n - 1]
    return f"{n}th"


async def cb_start_love(client: Client, callback: CallbackQuery):
    uid = callback.from_user.id
    acc_count = count_accounts(callback.from_user.id)

    if acc_count == 0:
        await callback.answer("🚫 First add an account!", show_alert=True)
        return

    clear_state(uid)
    set_state(uid, "awaiting_love_reason")

    await callback.message.edit_text(
        "<blockquote>"
        "❤️ <u>𝗦𝗧𝗔𝗥𝗧 𝗟𝗢𝗩𝗘</u>\n"
        "<b>💬 what is the reason for love?</b>\n\n"
        "<b>Examples:</b> <code>Spam</code>, <code>Fake Account</code>, <code>Voilance</code>, <code>Child Abuse</code>, <code>Pornography</code>, <code>Other</code>\n\n"
        "<b>🚫 Cancel:</b> /cancel"
        "</blockquote>",,
        parse_mode=ParseMode.HTML,
        reply_markup=kb_back_main()
    )


async def handle_love_flow(client: Client, message: Message):
    uid = message.from_user.id
    state = get_state(uid)
    if not state:
        return

    step = state["step"]
    data = state["data"]
    text = message.text.strip()

    # ── Step 1: Reason ───────────────────────────────────────
    if step == "awaiting_love_reason":
        update_data(uid, "reason", text)
        set_state(uid, "awaiting_love_count", data={"reason": text})

        await message.reply(
            f"<b>✅ Reason accepted:</b> <b>{text}</b>\n\n"
            "<b>❤️ how many times do you want to make love?</b>\n\n"
            "<b>Enter a number</b> (e.g. <code>10</code>):\n\n"
            "<b>🚫 Cancel:</b> /cancel"
        )

    # ── Step 2: Count ────────────────────────────────────────
    elif step == "awaiting_love_count":
        if not text.isdigit() or int(text) <= 0:
            await message.reply("⚠️ Just enter the positive number. Like: `5`")
            return

        count = int(text)
        reason = data.get("reason", "Love")
        acc_count = count_accounts()
        clear_state(uid)

        # Start printing love messages
        status_msg = await message.reply(
            f"<b>❤️ Love Starting...</b>\n\n"
            f"<b>💬 Reason: {reason}</b>\n"
            f"<b>🔢 Count: {count}</b>\n"
            f"<b>📱 Accounts: {acc_count}</b>\n\n"
            "─────────────────────"
        )

        love_lines = []
        for i in range(1, count + 1):
            ordinal = get_ordinal(i)
            line = f"{ordinal} love with {acc_count} account ❤️"
            love_lines.append(line)

            # Update message progressively
            display = "\n".join(love_lines)
            try:
                await status_msg.edit_text(
                    f"❤️ **Love in Progress...**\n\n"
                    f"💬 Reason: **{reason}**\n\n"
                    f"{display}"
                )
            except Exception:
                pass

            await asyncio.sleep(1)

        # Final message
        final_text = "\n".join(love_lines)
        await status_msg.edit_text(
            f"<b>❤️ Love Complete!</b>\n\n"
            f"<b>💬 Reason: {reason}</b>\n"
            f"{final_text}\n\n"
            "─────────────────────\n"
            "☠️ 𝗟𝗼𝘃𝗶𝗻𝗴 𝗰𝗼𝗺𝗽𝗹𝗲𝘁𝗲 𝘄𝗮𝗶𝘁 𝗳𝗼𝗿 𝘂𝗽𝘁𝗼 𝟭𝗵𝗿 𝘁𝗼 𝘀𝗲𝗲 𝘆𝗼𝘂𝗿 𝗿𝗲𝘀𝗽𝗼𝗻𝘀𝗲",
            reply_markup=kb_back_main()
        )
