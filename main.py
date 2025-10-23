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

# Initialize bot first
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# Import and initialize promotion service AFTER bot is defined
from services.promotion import init_promotion_service
promotion_service = init_promotion_service(bot)

# Import handlers AFTER promotion_service is initialized
from handlers.start import router as start_router
from handlers.admin import router as admin_router
from handlers.callback import router as callback_router
from handlers.group_events import router as group_router

# Set promotion_service in handlers
import handlers.admin
import handlers.group_events
handlers.admin.promotion_service = promotion_service
handlers.group_events.promotion_service = promotion_service

# Include routers
dp.include_router(start_router)
dp.include_router(admin_router)
dp.include_router(callback_router)
dp.include_router(group_router)

# Set bot for logger
Logger.set_bot(bot)

@dp.message(Command("test"))
async def test_handler(message: Message):
    await message.answer("✅ Bot is working!", parse_mode=ParseMode.HTML)

@dp.message(Command("check_promotion"))
async def check_promotion_handler(message: Message):
    """Check if promotion service is working"""
    if promotion_service:
        await message.answer("✅ Promotion service is working")
    else:
        await message.answer("❌ Promotion service is not available")

@dp.message(Command("help"))
async def help_handler(message: Message):
    """Show available commands"""
    help_text = """
<b>Available Commands:</b>

<code>/start</code> - Start the bot
<code>/manage</code> - Manage your groups and channels
<code>/setup</code> - Setup userbot in your channels
<code>/db</code> - Database management (Owner only)
<code>/stats</code> - Bot statistics (Owner only)
<code>/debug</code> - Debug information (Owner only)

<code>/check_permissions CHANNEL_ID</code> - Check bot permissions
<code>/manual_promote CHANNEL_ID</code> - Manually promote userbot
<code>/channel_info</code> - Check channel status
<code>/userbot_info</code> - Get userbot information
"""
    await message.answer(help_text, parse_mode=ParseMode.HTML)

async def main():
    print("🚀 Starting Auto Request Acceptor Bot...")
    
    # Start userbot
    await userbot_client.start()
    
    # Start main bot
    try:
        await dp.start_polling(bot)
        print("✅ Bot started successfully")
    except Exception as e:
        print(f"❌ Bot error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
