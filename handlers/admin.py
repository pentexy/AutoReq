from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode
from database.operations import db
from ui.buttons import ButtonManager
from userbot.client import userbot_client
from config import config
import asyncio

router = Router()

# This will be set by main.py
promotion_service = None

@router.message(Command("manage"))
async def manage_handler(message: Message):
    """Available to all users to manage their own chats"""
    user_id = message.from_user.id
    
    # Get chats added by this user
    user_chats = list(db.chats.find({"added_by": user_id}))
    
    if not user_chats:
        manage_text = """
<b>Chat Management</b>

You haven't added me to any groups/channels yet.

Add me to your group/channel and make me admin with:
- Manage Chat permission  
- Invite Users via link permission

Then use /manage to control your chats.
"""
        await message.answer(
            manage_text,
            reply_markup=ButtonManager.start_button(),
            parse_mode=ParseMode.HTML
        )
        return
    
    # Show user's chats
    total_chats = len(user_chats)
    groups = [c for c in user_chats if c['chat_type'] == 'group']
    channels = [c for c in user_chats if c['chat_type'] == 'channel']
    
    manage_text = f"""
<b>Your Chat Management</b>

<b>Your Groups:</b> {len(groups)}
<b>Your Channels:</b> {len(channels)}
<b>Total Chats:</b> {total_chats}

Select an option below to manage:
"""
    
    await message.answer(
        manage_text,
        reply_markup=ButtonManager.user_manage_main(),
        parse_mode=ParseMode.HTML
    )

@router.message(Command("db"))
async def db_handler(message: Message):
    """Owner-only full database management"""
    if message.from_user.id != config.OWNER_ID:
        return await message.answer("Owner only command")
    
    all_chats = db.get_all_chats()
    total_chats = len(all_chats)
    groups = [c for c in all_chats if c['chat_type'] == 'group']
    channels = [c for c in all_chats if c['chat_type'] == 'channel']
    
    stats_text = f"""
<b>Database Management (Owner)</b>

<b>Total Groups:</b> {len(groups)}
<b>Total Channels:</b> {len(channels)}
<b>Total Chats:</b> {total_chats}
"""
    
    await message.answer(
        stats_text,
        reply_markup=ButtonManager.db_main(),
        parse_mode=ParseMode.HTML
    )

@router.message(Command("stats"))
async def stats_handler(message: Message):
    if message.from_user.id != config.OWNER_ID:
        return
    
    all_chats = db.get_all_chats()
    groups = [chat for chat in all_chats if chat['chat_type'] == 'group']
    channels = [chat for chat in all_chats if chat['chat_type'] == 'channel']
    
    stats_text = f"""
<b>Overall Statistics (Owner)</b>

<b>Groups:</b> {len(groups)}
<b>Channels:</b> {len(channels)}
<b>Total Chats:</b> {len(all_chats)}

<b>Active Chats:</b> {len([c for c in all_chats if c.get('is_active', True)])}
"""
    
    await message.answer(stats_text, parse_mode=ParseMode.HTML)

@router.message(Command("debug"))
async def debug_handler(message: Message):
    if message.from_user.id != config.OWNER_ID:
        return
    
    all_chats = db.get_all_chats()
    total_chats = len(all_chats)
    active_chats = len([c for c in all_chats if c.get('is_active', True)])
    
    debug_text = f"""
<b>Debug Information</b>

<b>Total Chats in DB:</b> {total_chats}
<b>Active Chats:</b> {active_chats}
<b>Bot Status:</b> Running
<b>Userbot Status:</b> {'Connected' if userbot_client.is_connected else 'Disconnected'}

<b>Recent Chats:</b>
"""
    
    for chat in all_chats[-5:]:
        status = "Active" if chat.get('is_active', True) else "Inactive"
        debug_text += f"• {chat['title']} ({chat['chat_type']}) - {status}\n"
    
    await message.answer(debug_text, parse_mode=ParseMode.HTML)

# ... (keep all the other handlers you have for setup, check_permissions, etc.)
