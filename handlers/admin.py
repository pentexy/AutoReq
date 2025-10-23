from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from database.operations import MongoDB
from ui.buttons import ButtonManager
from config import config

router = Router()
db = MongoDB()

@router.message(Command("db"))
async def db_handler(message: Message):
    if message.from_user.id != config.OWNER_ID:
        return await message.answer("❌ Owner only command")
    
    stats_text = """
📊 **Database Management**

View and manage all groups/channels where I'm added.
"""
    
    await message.answer(
        stats_text,
        reply_markup=ButtonManager.db_main()
    )

@router.message(Command("stats"))
async def stats_handler(message: Message):
    if message.from_user.id != config.OWNER_ID:
        return
    
    all_chats = db.get_all_chats()
    groups = [chat for chat in all_chats if chat['chat_type'] == 'group']
    channels = [chat for chat in all_chats if chat['chat_type'] == 'channel']
    
    stats_text = f"""
📈 **Overall Statistics**

**Groups:** {len(groups)}
**Channels:** {len(channels)}
**Total Chats:** {len(all_chats)}

**Active Chats:** {len([c for c in all_chats if c.get('is_active', True)])}
"""
    
    await message.answer(stats_text)
