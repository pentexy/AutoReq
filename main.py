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
from database.operations import MongoDB
from utils.logger import Logger
from userbot.client import userbot_client

# Initialize
app = Client(
    "auto_req_bot", 
    api_id=config.API_ID, 
    api_hash=config.API_HASH, 
    bot_token=config.BOT_TOKEN
)
db = MongoDB()

# Import and register handlers manually
from handlers.start import start_handler
from handlers.admin import db_handler, stats_handler
from handlers.callback import callback_handler

# Register handlers manually
app.on_message(filters.command("start") & filters.private)(start_handler)
app.on_message(filters.command("db") & filters.private)(db_handler)
app.on_message(filters.command("stats") & filters.private)(stats_handler)
app.on_callback_query()(callback_handler)

@app.on_chat_join_request()
async def chat_join_request_handler(client: Client, request: ChatJoinRequest):
    try:
        chat = request.chat
        user = request.from_user
        
        logger.info(f"Join request from {user.id} in {chat.title}")
        
        # Save request to database
        request_data = {
            "chat_id": str(chat.id),
            "user_id": user.id,
            "username": user.username or "",
            "first_name": user.first_name or ""
        }
        db.add_request(request_data)
        
        # Update chat stats
        stats = db.get_chat_stats(str(chat.id))
        db.update_chat_stats(str(chat.id), stats)
        
        # Auto-accept if enabled
        chat_data = db.get_chat(str(chat.id))
        if chat_data and chat_data.is_active:
            success = await userbot_client.accept_chat_join_request(str(chat.id), user.id)
            if success:
                db.update_request_status(str(chat.id), user.id, "accepted")
                await Logger.log_request_accepted(client, chat.title, user.username or user.first_name)
        
    except Exception as e:
        logger.error(f"Join request error: {e}")
        await Logger.log_error(client, f"Join request error: {e}")

@app.on_message(filters.new_chat_members)
async def new_chat_member_handler(client: Client, message: Message):
    try:
        for user in message.new_chat_members:
            if user.is_self:  # Bot added to group/channel
                chat = message.chat
                added_by = message.from_user.id
                
                logger.info(f"Bot added to {chat.title} by {added_by}")
                
                # Save to database
                chat_data = {
                    "chat_id": str(chat.id),
                    "title": chat.title,
                    "chat_type": "group" if chat.type in ["group", "supergroup"] else "channel",
                    "added_by": added_by
                }
                
                db.add_chat(chat_data)
                
                # Send DM to user who added bot
                try:
                    dm_text = f"""
**Thanks for adding me to {chat.title}!**

I've been successfully added to your {chat_data['chat_type']} and saved in my database.

Use /db command in my DM to manage this {chat_data['chat_type']}.
"""
                    await client.send_message(added_by, dm_text)
                except Exception as e:
                    logger.warning(f"Could not send DM to {added_by}: {e}")
                
                # Log to owner
                await Logger.log_chat_added(client, chat.title, added_by, chat_data['chat_type'])
                
    except Exception as e:
        logger.error(f"New chat member error: {e}")
        await Logger.log_error(client, f"New chat member error: {e}")

# Add a simple test handler
@app.on_message(filters.private & filters.text)
async def test_handler(client: Client, message: Message):
    logger.info(f"Received: {message.text} from {message.from_user.id}")
    if message.text.lower() == "ping":
        await message.reply_text("🏓 Pong! Bot is working!")

async def main():
    try:
        # Start userbot
        userbot_started = await userbot_client.start()
        if userbot_started:
            print("✅ Userbot started successfully")
        else:
            print("⚠️ Userbot not started (session not configured)")
        
        # Start main bot
        print("🤖 Starting Auto Request Acceptor Bot...")
        await app.start()
        
        me = await app.get_me()
        print(f"✅ Bot started successfully: @{me.username}")
        print(f"🆔 Bot ID: {me.id}")
        print("📱 Bot is now running and listening for commands...")
        print("💡 Try sending /start to your bot")
        
        # Keep running
        await asyncio.Event().wait()
        
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
    finally:
        await app.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("❌ Bot stopped by user")
