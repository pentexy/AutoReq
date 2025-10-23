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
        
        # Test with current chat
        try:
            chat_member = await bot.get_chat_member(message.chat.id, bot.id)
            if chat_member.status == ChatMemberStatus.ADMINISTRATOR:
                await message.answer("✅ Bot is admin in this chat")
            else:
                await message.answer("❌ Bot is NOT admin in this chat")
        except Exception as e:
            await message.answer(f"❌ Error checking admin status: {e}")
    else:
        await message.answer("❌ Promotion service is not available")

@dp.message(Command("promote_test"))
async def promote_test_handler(message: Message):
    """Test promotion in current chat"""
    if not promotion_service:
        await message.answer("❌ Promotion service not available")
        return
    
    # Get userbot info
    userbot_info = await userbot_client.get_userbot_info()
    if not userbot_info:
        await message.answer("❌ Could not get userbot info")
        return
    
    await message.answer(f"Testing promotion for userbot {userbot_info['id']}...")
    
    success = await promotion_service.promote_userbot(message.chat.id, userbot_info['id'])
    
    if success:
        await message.answer("✅ Promotion test successful!")
    else:
        await message.answer("❌ Promotion test failed")

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
