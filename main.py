import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

from config import config
from database.operations import db
from userbot.client import userbot_client
from utils.logger import Logger

# Import and initialize promotion service
from services.promotion import init_promotion_service

# Initialize bot
bot = Bot(token=config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Initialize promotion service
promotion_service = init_promotion_service(bot)

# Import and register handlers
from handlers import start, admin, callback, group_events

# Register all handlers
start.register_handlers(dp)
admin.register_handlers(dp)
callback.register_handlers(dp)
group_events.register_handlers(dp)

# Set bot for logger
Logger.set_bot(bot)

@dp.message_handler(commands=['test'])
async def test_handler(message: types.Message):
    await message.answer("✅ Bot is working!")

@dp.message_handler(commands=['check_promotion'])
async def check_promotion_handler(message: types.Message):
    """Check if promotion service is working"""
    if promotion_service:
        await message.answer("✅ Promotion service is working")
    else:
        await message.answer("❌ Promotion service is not available")

@dp.message_handler(commands=['help'])
async def help_handler(message: types.Message):
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
    await message.answer(help_text, parse_mode='HTML')

async def on_startup(dp):
    print("🚀 Starting Auto Request Acceptor Bot...")
    # Start userbot
    await userbot_client.start()

async def on_shutdown(dp):
    await bot.session.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
