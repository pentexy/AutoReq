from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode
from database.operations import db
from ui.buttons import ButtonManager
from userbot.client import userbot_client
import asyncio

router = Router()

@router.callback_query(F.data == "db_main")
async def db_main_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        "<b>📊 Database Management</b>\nSelect category:",
        reply_markup=ButtonManager.db_main(),
        parse_mode=ParseMode.HTML
    )

@router.callback_query(F.data.startswith("db_"))
async def db_category_callback(callback: CallbackQuery):
    chat_type = callback.data.replace("db_", "")
    await show_chat_list(callback, chat_type)

@router.callback_query(F.data.startswith("list_"))
async def list_page_callback(callback: CallbackQuery):
    parts = callback.data.split("_")
    chat_type = parts[1]
    page = int(parts[2])
    await show_chat_list(callback, chat_type, page)

@router.callback_query(F.data.startswith("chat_"))
async def chat_detail_callback(callback: CallbackQuery):
    chat_id = callback.data.replace("chat_", "")
    await show_chat_detail(callback, chat_id)

@router.callback_query(F.data.startswith("accept_all_"))
async def accept_all_callback(callback: CallbackQuery):
    chat_id = callback.data.replace("accept_all_", "")
    await accept_all_requests(callback, chat_id)

async def show_chat_list(callback: CallbackQuery, chat_type: str, page: int = 0):
    all_chats = db.get_chats_by_type(chat_type)
    
    if not all_chats:
        await callback.message.edit_text(
            f"No {chat_type}s found in database.",
            reply_markup=ButtonManager.back_button("db_main")
        )
        return
    
    text = f"<b>{chat_type.title()}s</b>\n\nSelect a chat to view details:"
    await callback.message.edit_text(
        text,
        reply_markup=ButtonManager.chat_list(all_chats, page, chat_type),
        parse_mode=ParseMode.HTML
    )

async def show_chat_detail(callback: CallbackQuery, chat_id: str):
    chat = db.get_chat(chat_id)
    if not chat:
        await callback.answer("Chat not found!", show_alert=True)
        return
    
    stats = db.get_chat_stats(chat_id)
    
    text = f"""
<b>Chat Details</b>

<b>Title:</b> {chat['title']}
<b>Type:</b> {chat['chat_type']}
<b>ID:</b> {chat['chat_id']}
<b>Added By:</b> {chat['added_by']}

<b>Statistics:</b>
Total Requests: {stats['total_requests']}
Pending: {stats['pending_requests']}
Accepted: {stats['accepted_requests']}
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=ButtonManager.chat_detail(chat_id, stats),
        parse_mode=ParseMode.HTML
    )

async def accept_all_requests(callback: CallbackQuery, chat_id: str):
    await callback.message.edit_text("Starting to accept all requests...")
    
    pending_requests = db.get_pending_requests(chat_id)
    if not pending_requests:
        await callback.message.edit_text("No pending requests found.")
        return
    
    success_count = 0
    for request in pending_requests:
        try:
            result = await userbot_client.accept_join_request(int(chat_id), request['user_id'])
            if result:
                db.update_request_status(chat_id, request['user_id'], "accepted")
                success_count += 1
                await asyncio.sleep(1)  # Rate limit
        except Exception as e:
            print(f"Error accepting request: {e}")
    
    await callback.message.edit_text(f"Accepted {success_count} requests successfully.")
