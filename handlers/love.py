import asyncio
from pyrogram import Client
from pyrogram.types import Message, CallbackQuery
from utils.keyboards import kb_back_main, kb_main_menu
from utils.state import set_state, get_state, update_data, clear_state
from database.db import count_accounts

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
    acc_count = count_accounts()

    if acc_count == 0:
        await callback.answer("❌ Pehle koi account add karo!", show_alert=True)
        return

    clear_state(uid)
    set_state(uid, "awaiting_love_reason")

    await callback.message.edit_text(
        "❤️ **Start Love**\n\n"
        "💬 Love ka reason kya hai?\n\n"
        "Examples: `Propose`, `Hate`, `Marry`, `Friendship`\n\n"
        "❌ Cancel: /cancel",
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
            f"✅ Reason accepted: **{text}**\n\n"
            "❤️ **Kitni baar love karna chahte ho?**\n\n"
            "Ek number enter karo (jaise: `6`):\n\n"
            "❌ Cancel: /cancel"
        )

    # ── Step 2: Count ────────────────────────────────────────
    elif step == "awaiting_love_count":
        if not text.isdigit() or int(text) <= 0:
            await message.reply("⚠️ Sirf positive number enter karo. Jaise: `5`")
            return

        count = int(text)
        reason = data.get("reason", "Love")
        acc_count = count_accounts()
        clear_state(uid)

        # Start printing love messages
        status_msg = await message.reply(
            f"❤️ **Love Starting...**\n\n"
            f"💬 Reason: **{reason}**\n"
            f"🔢 Count: **{count}**\n"
            f"📱 Accounts: **{acc_count}**\n\n"
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
            f"❤️ **Love Complete!**\n\n"
            f"💬 Reason: **{reason}**\n\n"
            f"{final_text}\n\n"
            "─────────────────────\n"
            "☠️ **Loving complete wait for upto 1hr to see your response**",
            reply_markup=kb_back_main()
        )
