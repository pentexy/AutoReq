import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from config import config
from database.operations import MongoDB
from userbot.client import userbot_client
from utils.logger import Logger

# Import handlers
from handlers.start import router as start_router
from handlers.admin import router as admin_router
from handlers.callback import router as callback_router

# Initialize
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()
db = MongoDB()

# Include routers
dp.include_router(start_router)
dp.include_router(admin_router)
dp.include_router(callback_router)

# Set bot for logger
Logger.set_bot(bot)

@dp.message(Command("test"))
async def test_handler(message: Message):
    await message.answer("✅ Bot is working!")

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
