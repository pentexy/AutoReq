from pyrogram import Client, filters
from pyrogram.types import Message
from database.operations import MongoDB
from ui.buttons import ButtonManager
from utils.logger import Logger
from config import config

db = MongoDB()

@Client.on_message(filters.command("db") & filters.user(config.OWNER_ID))
async def db_handler(client: Client, message: Message):
    stats_text = """
**Database Management**

View and manage all groups/channels where I'm added.
"""
    
    await message.reply_text(
        stats_text,
        reply_markup=ButtonManager.db_main()
    )

@Client.on_message(filters.command("stats") & filters.user(config.OWNER_ID))
async def stats_handler(client: Client, message: Message):
    all_chats = db.get_all_chats()
    groups = [chat for chat in all_chats if chat.chat_type == "group"]
    channels = [chat for chat in all_chats if chat.chat_type == "channel"]
    
    stats_text = f"""
**Overall Statistics**

**Groups:** {len(groups)}
**Channels:** {len(channels)}
**Total Chats:** {len(all_chats)}

**Active Chats:** {len([c for c in all_chats if c.is_active])}
**Admin Status:** {len([c for c in all_chats if c.is_admin])}
"""
    
    await message.reply_text(stats_text)
