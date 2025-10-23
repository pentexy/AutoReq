from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode
from database.operations import db
from ui.buttons import ButtonManager
from config import config

router = Router()

@router.message(Command("db"))
async def db_handler(message: Message):
    if message.from_user.id != config.OWNER_ID:
        return await message.answer("❌ Owner only command")
    
    stats_text = """
<b>📊 Database Management</b>

View and manage all groups/channels where I'm added.
"""
    
    await message.answer(
        stats_text,
        reply_markup=ButtonManager.db_main(),
        parse_mode=ParseMode.HTML
    )

@router.message(Command("debug"))
async def debug_handler(message: Message):
    if message.from_user.id != config.OWNER_ID:
        return
    
    all_chats = db.get_all_chats()
    total_chats = len(all_chats)
    active_chats = len([c for c in all_chats if c.get('is_active', True)])
    
    debug_text = f"""
<b>🔧 Debug Information</b>

<b>Total Chats in DB:</b> {total_chats}
<b>Active Chats:</b> {active_chats}
<b>Bot Status:</b> ✅ Running
<b>Userbot Status:</b> {'✅ Connected' if userbot_client.is_connected else '❌ Disconnected'}

<b>Recent Chats:</b>
"""
    
    for chat in all_chats[-5:]:  # Show last 5 chats
        debug_text += f"• {chat['title']} ({chat['chat_type']})\n"
    
    await message.answer(debug_text, parse_mode=ParseMode.HTML)

@router.message(Command("stats"))
async def stats_handler(message: Message):
    if message.from_user.id != config.OWNER_ID:
        return
    
    all_chats = db.get_all_chats()
    groups = [chat for chat in all_chats if chat['chat_type'] == 'group']
    channels = [chat for chat in all_chats if chat['chat_type'] == 'channel']
    
    stats_text = f"""
<b>📈 Overall Statistics</b>

<b>Groups:</b> {len(groups)}
<b>Channels:</b> {len(channels)}
<b>Total Chats:</b> {len(all_chats)}

<b>Active Chats:</b> {len([c for c in all_chats if c.get('is_active', True)])}
"""
    
    await message.answer(stats_text, parse_mode=ParseMode.HTML)
