from pyrogram import Client
from pyrogram.types import Message, CallbackQuery
from utils.keyboards import kb_target_menu, kb_target_save, kb_back_main
from utils.state import set_state, get_state, update_data, clear_state
from database.db import save_target, get_target, delete_target
from pyrogram.enums import ParseMode

async def cb_target_menu(client: Client, callback: CallbackQuery):
    target = get_target()
    clear_state(callback.from_user.id)

    if target:
        text = (
            "🎯 **Current Target**\n\n"
            f"👤 Name: {target.get('name', 'N/A')}\n"
            f"🆔 User ID: `{target.get('id', 'N/A')}`\n"
            f"🔗 Username: @{target.get('username', 'N/A')}\n\n"
            "To set a new target, delete it first.."
        )
    else:
        text = (
            "🎯 **Target**\n\n"
            "🚫 No target is set.\n"
            "Set the target from the button below."
        )

    await callback.message.edit_text(text, reply_markup=kb_target_menu(bool(target)))


async def cb_set_target(client: Client, callback: CallbackQuery):
    uid = callback.from_user.id
    set_state(uid, "awaiting_target_input")
    await callback.message.edit_text(
        "<blockquote>"
        "🔍 <b><u>Set Your Target</u></b>\n\n"
        "Enter username:\n"
        "Example: <code>@username</code> \n\n"
        "🚫 Cancel: /cancel"
        "</blockquote>",
        parse_mode=ParseMode.HTML,
        reply_markup=kb_back_main()
    )


async def handle_target_flow(client: Client, message: Message):
    uid = message.from_user.id
    state = get_state(uid)
    if not state or state["step"] != "awaiting_target_input":
        return

    text = message.text.strip()

    try:
        user = await client.get_users(text)
        full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        info = {
            "name": full_name,
            "id": user.id,
            "username": user.username or "N/A"
        }
        update_data(uid, "target_info", info)
        set_state(uid, "confirm_target", data={"target_info": info})

        await message.reply(
            "<blockquote>"
            f"👤 <b>User Found!<b>\n\n"
            f"👤 Name: {full_name}\n"
            f"🆔 User ID: `{user.id}`\n"
            f"🔗 Username: @{user.username or 'N/A'}\n\n"
            "Do you want to save your target with this?"
            "</blockquote>",
            parse_mode=ParseMode.HTML,
            reply_markup=kb_target_save()
        )
    except Exception as e:
        await message.reply(
            f"❌ User not found: `{e}`\n\nTry again.",
            reply_markup=kb_back_main()
        )


async def cb_save_target(client: Client, callback: CallbackQuery):
    uid = callback.from_user.id
    state = get_state(uid)

    if not state or "target_info" not in state.get("data", {}):
        await callback.answer("❌ No data found. Try again..", show_alert=True)
        return

    info = state["data"]["target_info"]
    save_target(info)
    clear_state(uid)

    await callback.answer("✅ Target saved!", show_alert=True)
    await callback.message.edit_text(
        f"✅ **Target Saved!**\n\n"
        f"👤 Name: {info['name']}\n"
        f"🆔 User ID: `{info['id']}`\n"
        f"🔗 Username: @{info['username']}",
        reply_markup=kb_target_menu(True)
    )


async def cb_delete_target(client: Client, callback: CallbackQuery):
    delete_target()
    await callback.answer("🗑 Target deleted!", show_alert=True)
    await callback.message.edit_text(
        "🎯 **Target**\n\n🚫 No target is set.\nSet target using the button below.",
        reply_markup=kb_target_menu(False)
    )
