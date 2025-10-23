from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode
from ui.buttons import ButtonManager
from utils.logger import Logger
from config import config

router = Router()

@router.message(Command("start"))
async def start_handler(message: Message):
    user_id = message.from_user.id
    
    welcome_text = """
<b> Auto Request Acceptor Bot</b>

Add me to your group/channel and make me admin with:
• Manage Chat permission
• Invite Users via link permission

I will automatically accept join requests and log everything.

After adding me, use <code>/manage</code> to control your chats.
"""
    
    await message.answer(
        welcome_text,
        reply_markup=ButtonManager.start_button(),
        parse_mode=ParseMode.HTML
    )
    
    # Log to owner
    await Logger.log_to_owner(
        f"User started bot: {message.from_user.full_name}\nID: {user_id}"
    )
