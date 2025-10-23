from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest, Message
from config import config
from database.operations import MongoDB
from utils.logger import Logger
from userbot.client import userbot_client
import asyncio

# Import handlers
from handlers.start import start_handler
from handlers.admin import db_handler, stats_handler
from handlers.callback import callback_handler

# Initialize
app = Client("auto_req_bot", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN)
db = MongoDB()

@app.on_chat_join_request()
async def chat_join_request_handler(client: Client, request: ChatJoinRequest):
    try:
        chat = request.chat
        user = request.from_user
        
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
        await Logger.log_error(client, f"Join request error: {e}")

@app.on_message(filters.new_chat_members)
async def new_chat_member_handler(client: Client, message: Message):
    try:
        for user in message.new_chat_members:
            if user.is_self:  # Bot added to group/channel
                chat = message.chat
                added_by = message.from_user.id
                
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
                except:
                    pass  # Can't send DM if user blocked bot
                
                # Log to owner
                await Logger.log_chat_added(client, chat.title, added_by, chat_data['chat_type'])
                
    except Exception as e:
        await Logger.log_error(client, f"New chat member error: {e}")

async def main():
    # Start userbot
    await userbot_client.start()
    
    # Start main bot
    print("Starting Auto Request Acceptor Bot...")
    await app.start()
    print("Bot started successfully!")
    
    # Keep running
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
