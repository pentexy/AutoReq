from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from database.operations import MongoDB
from ui.buttons import ButtonManager
from utils.logger import Logger
from userbot.client import UserBotClient
import asyncio

db = MongoDB()
userbot = UserBotClient()

@Client.on_callback_query()
async def callback_handler(client: Client, callback: CallbackQuery):
    data = callback.data
    
    if data == "db_main":
        await callback.edit_message_text(
            "**Database Management**\nSelect category:",
            reply_markup=ButtonManager.db_main()
        )
    
    elif data.startswith("db_"):
        chat_type = data.replace("db_", "")
        await show_chat_list(callback, chat_type)
    
    elif data.startswith("list_"):
        parts = data.split("_")
        chat_type = parts[1]
        page = int(parts[2])
        await show_chat_list(callback, chat_type, page)
    
    elif data.startswith("chat_"):
        chat_id = data.replace("chat_", "")
        await show_chat_detail(client, callback, chat_id)
    
    elif data.startswith("accept_all_"):
        chat_id = data.replace("accept_all_", "")
        await accept_all_requests(client, callback, chat_id)
    
    await callback.answer()

async def show_chat_list(callback: CallbackQuery, chat_type: str, page: int = 0):
    all_chats = db.get_all_chats()
    filtered_chats = [chat for chat in all_chats if chat.chat_type == chat_type]
    
    if not filtered_chats:
        await callback.edit_message_text(
            f"No {chat_type}s found in database.",
            reply_markup=ButtonManager.back_button("db_main")
        )
        return
    
    text = f"**{chat_type.title()}s**\n\nSelect a chat to view details:"
    await callback.edit_message_text(
        text,
        reply_markup=ButtonManager.chat_list(filtered_chats, page, chat_type)
    )

async def show_chat_detail(client: Client, callback: CallbackQuery, chat_id: str):
    chat = db.get_chat(chat_id)
    if not chat:
        await callback.answer("Chat not found!", show_alert=True)
        return
    
    stats = db.get_chat_stats(chat_id)
    
    text = f"""
**Chat Details**

**Title:** {chat.title}
**Type:** {chat.chat_type}
**ID:** {chat.chat_id}
**Added By:** {chat.added_by}
**Status:** {'Active' if chat.is_active else 'Inactive'}
**Admin:** {'Yes' if chat.is_admin else 'No'}

**Statistics:**
Total Requests: {stats['total_requests']}
Pending: {stats['pending_requests']}
Accepted: {stats['accepted_requests']}
"""
    
    await callback.edit_message_text(
        text,
        reply_markup=ButtonManager.chat_detail(chat_id, stats)
    )

async def accept_all_requests(client: Client, callback: CallbackQuery, chat_id: str):
    await callback.edit_message_text("Starting to accept all requests...")
    
    pending_requests = db.get_pending_requests(chat_id)
    if not pending_requests:
        await callback.edit_message_text("No pending requests found.")
        return
    
    success_count = 0
    for request in pending_requests:
        try:
            # Use userbot to accept request
            result = await userbot.accept_chat_join_request(chat_id, request.user_id)
            if result:
                db.update_request_status(chat_id, request.user_id, "accepted")
                success_count += 1
                await asyncio.sleep(1)  # Rate limit
        except Exception as e:
            await Logger.log_error(client, f"Error accepting request: {e}")
    
    await callback.edit_message_text(f"Accepted {success_count} requests successfully.")
