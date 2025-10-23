from pyrogram import Client, filters
from pyrogram.types import Message
from ui.buttons import ButtonManager
from utils.logger import Logger
from config import config
import logging

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    user_id = message.from_user.id
    
    logger.info(f"Start command received from {user_id}")
    
    if len(message.command) > 1:
        # Handle deep linking
        pass
    
    welcome_text = """
**Auto Request Acceptor Bot**

Add me to your group/channel and make me admin with:
- Manage Chat permission
- Invite Users via link permission

I will automatically accept join requests and log everything.
"""
    
    await message.reply_text(
        welcome_text,
        reply_markup=ButtonManager.start_button()
    )
    
    # Log to owner
    await Logger.log_to_owner(
        client,
        f"User started bot: {message.from_user.mention}\nID: {user_id}"
    )
