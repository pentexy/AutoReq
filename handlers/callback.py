from config import config
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode
from database.operations import db
from ui.buttons import ButtonManager
from userbot.client import userbot_client
import asyncio

router = Router()

# User management callbacks
@router.callback_query(F.data == "my_main")
async def my_main_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_chats = list(db.chats.find({"added_by": user_id}))
    
    groups = [c for c in user_chats if c['chat_type'] == 'group']
    channels = [c for c in user_chats if c['chat_type'] == 'channel']
    
    text = f"""
<b>📊 Your Chat Management</b>

<b>Your Groups:</b> {len(groups)}
<b>Your Channels:</b> {len(channels)}
<b>Total Chats:</b> {len(user_chats)}

Select an option below to manage:
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=ButtonManager.user_manage_main(),
        parse_mode=ParseMode.HTML
    )

@router.callback_query(F.data.startswith("my_"))
async def my_category_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    data = callback.data
    
    if data == "my_groups":
        chat_type = "group"
        list_type = "my_groups"
    elif data == "my_channels":
        chat_type = "channel"
        list_type = "my_channels"
    else:
        return
    
    # Get only user's chats
    user_chats = list(db.chats.find({
        "added_by": user_id,
        "chat_type": chat_type
    }))
    
    await show_chat_list(callback, user_chats, list_type, 0, is_owner=False)

# Owner management callbacks
@router.callback_query(F.data == "db_main")
async def db_main_callback(callback: CallbackQuery):
    if callback.from_user.id != config.OWNER_ID:
        await callback.answer("Owner only!", show_alert=True)
        return
    
    all_chats = db.get_all_chats()
    groups = [c for c in all_chats if c['chat_type'] == 'group']
    channels = [c for c in all_chats if c['chat_type'] == 'channel']
    
    text = f"""
<b>📊 Database Management (Owner)</b>

<b>Total Groups:</b> {len(groups)}
<b>Total Channels:</b> {len(channels)}
<b>Total Chats:</b> {len(all_chats)}
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=ButtonManager.db_main(),
        parse_mode=ParseMode.HTML
    )

@router.callback_query(F.data.startswith("db_"))
async def db_category_callback(callback: CallbackQuery):
    if callback.from_user.id != config.OWNER_ID:
        await callback.answer("Owner only!", show_alert=True)
        return
    
    data = callback.data
    if data == "db_groups":
        chat_type = "group"
        list_type = "db_groups"
    elif data == "db_channels":
        chat_type = "channel"
        list_type = "db_channels"
    elif data == "db_users":
        await show_user_stats(callback)
        return
    else:
        return
    
    all_chats = db.get_chats_by_type(chat_type)
    await show_chat_list(callback, all_chats, list_type, 0, is_owner=True)

@router.callback_query(F.data.startswith("list_"))
async def list_page_callback(callback: CallbackQuery):
    parts = callback.data.split("_")
    list_type = f"{parts[1]}_{parts[2]}"  # my_groups, db_channels, etc
    page = int(parts[3])
    
    if list_type.startswith("my_"):
        # User's chats
        user_id = callback.from_user.id
        chat_type = list_type.replace("my_", "")
        user_chats = list(db.chats.find({
            "added_by": user_id,
            "chat_type": chat_type
        }))
        await show_chat_list(callback, user_chats, list_type, page, is_owner=False)
    else:
        # Owner's all chats
        if callback.from_user.id != config.OWNER_ID:
            await callback.answer("Owner only!", show_alert=True)
            return
        
        chat_type = list_type.replace("db_", "")
        all_chats = db.get_chats_by_type(chat_type)
        await show_chat_list(callback, all_chats, list_type, page, is_owner=True)

@router.callback_query(F.data.startswith("chat_"))
async def chat_detail_callback(callback: CallbackQuery):
    chat_id = callback.data.replace("chat_", "")
    chat = db.get_chat(chat_id)
    
    if not chat:
        await callback.answer("Chat not found!", show_alert=True)
        return
    
    # Check if user has permission to view this chat
    user_id = callback.from_user.id
    is_owner = (user_id == config.OWNER_ID)
    is_chat_owner = (user_id == chat['added_by'])
    
    if not (is_owner or is_chat_owner):
        await callback.answer("You don't have permission to view this chat!", show_alert=True)
        return
    
    stats = db.get_chat_stats(chat_id)
    
    text = f"""
<b>Chat Details</b>

<b>Title:</b> {chat['title']}
<b>Type:</b> {chat['chat_type']}
<b>ID:</b> {chat['chat_id']}
<b>Added By:</b> {chat['added_by']}
<b>Status:</b> {'✅ Active' if chat.get('is_active', True) else '❌ Inactive'}

<b>Statistics:</b>
Total Requests: {stats['total_requests']}
Pending: {stats['pending_requests']}
Accepted: {stats['accepted_requests']}
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=ButtonManager.chat_detail(chat_id, stats, is_owner=is_owner),
        parse_mode=ParseMode.HTML
    )

async def show_chat_list(callback: CallbackQuery, chats, list_type: str, page: int = 0, is_owner: bool = False):
    if not chats:
        await callback.message.edit_text(
            f"No chats found.",
            reply_markup=ButtonManager.back_button("my_main" if list_type.startswith("my_") else "db_main")
        )
        return
    
    prefix = "Your" if list_type.startswith("my_") else "All"
    chat_type = list_type.replace("my_", "").replace("db_", "")
    
    text = f"<b>{prefix} {chat_type.title()}s</b>\n\nSelect a chat to view details:"
    await callback.message.edit_text(
        text,
        reply_markup=ButtonManager.chat_list(chats, page, list_type),
        parse_mode=ParseMode.HTML
    )

async def show_user_stats(callback: CallbackQuery):
    if callback.from_user.id != config.OWNER_ID:
        return
    
    # Get all unique users who added the bot
    pipeline = [
        {"$group": {"_id": "$added_by", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    user_stats = list(db.chats.aggregate(pipeline))
    
    text = "<b>👥 User Statistics</b>\n\n"
    for stat in user_stats[:10]:  # Top 10 users
        text += f"User {stat['_id']}: {stat['count']} chats\n"
    
    await callback.message.edit_text(text, parse_mode=ParseMode.HTML)

@router.callback_query(F.data.startswith("accept_all_"))
async def accept_all_callback(callback: CallbackQuery):
    chat_id = callback.data.replace("accept_all_", "")
    await accept_all_requests(callback, chat_id)

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
