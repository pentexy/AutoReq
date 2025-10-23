import os
import asyncio
import logging
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest, Message
from config import config

# Initialize bot
app = Client(
    "auto_req_bot", 
    api_id=config.API_ID, 
    api_hash=config.API_HASH, 
    bot_token=config.BOT_TOKEN
)

# Add handlers directly in main.py
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    logger.info(f"Start command from {message.from_user.id}")
    
    welcome_text = """
**Auto Request Acceptor Bot**

Add me to your group/channel and make me admin with:
- Manage Chat permission  
- Invite Users via link permission

I will automatically accept join requests.
"""
    await message.reply_text(welcome_text)

@app.on_message(filters.command("db") & filters.private & filters.user(config.OWNER_ID))
async def db_handler(client: Client, message: Message):
    logger.info(f"DB command from {message.from_user.id}")
    await message.reply_text("📊 Database management")

@app.on_message(filters.private & filters.text)
async def echo_handler(client: Client, message: Message):
    logger.info(f"Message from {message.from_user.id}: {message.text}")
    await message.reply_text(f"Echo: {message.text}")

async def main():
    try:
        # Start main bot
        print("🤖 Starting Bot...")
        await app.start()
        
        me = await app.get_me()
        print(f"✅ Bot started: @{me.username}")
        print("📱 Send /start to test")
        
        # Keep running
        await asyncio.Event().wait()
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
