import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode

from config import config
from database.operations import db
from userbot.client import userbot_client
from utils.logger import Logger

# Import handlers
from handlers.start import router as start_router
from handlers.admin import router as admin_router
from handlers.callback import router as callback_router
from handlers.group_events import router as group_router  # Add this line

# Initialize
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# Include routers
dp.include_router(start_router)
dp.include_router(admin_router)
dp.include_router(callback_router)
dp.include_router(group_router)  # Add this line

# Set bot for logger
Logger.set_bot(bot)

@dp.message(Command("test"))
async def test_handler(message: Message):
    await message.answer("✅ Bot is working!", parse_mode=ParseMode.HTML)

@dp.message(Command("chats"))
async def chats_handler(message: Message):
    if message.from_user.id != config.OWNER_ID:
        return
    
    all_chats = db.get_all_chats()
    if not all_chats:
        await message.answer("No chats in database yet.")
        return
    
    text = "<b>📊 All Chats in Database:</b>\n\n"
    for chat in all_chats:
        text += f"• {chat['title']} ({chat['chat_type']}) - {chat['chat_id']}\n"
    
    await message.answer(text, parse_mode=ParseMode.HTML)

async def main():
    print("🚀 Starting Auto Request Acceptor Bot...")
    
    # Start userbot
    await userbot_client.start()
    
    # Start main bot
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ Bot error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
