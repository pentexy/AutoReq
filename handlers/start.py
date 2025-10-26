from aiogram import Dispatcher, types
from aiogram.dispatcher import filters
from ui.buttons import ButtonManager
from utils.logger import Logger
from config import config

async def start_handler(message: types.Message):
    user_id = message.from_user.id
    
    welcome_text = """
🤖 **Auto Request Acceptor Bot**

Add me to your group/channel and make me admin with:
• Manage Chat permission
• Invite Users via link permission

I will automatically accept join requests and log everything.

After adding me, use <code>/manage</code> to control your chats.
"""
    
    await message.answer(
        welcome_text,
        reply_markup=ButtonManager.start_button(),
        parse_mode='HTML'
    )
    
    # Log to owner
    await Logger.log_to_owner(
        f"User started bot: {message.from_user.full_name}\nID: {user_id}"
    )

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_handler, commands=['start'])
