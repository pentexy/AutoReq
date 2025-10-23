from pyrogram import Client
from config import config

class Logger:
    @staticmethod
    async def log_to_owner(client: Client, message: str):
        try:
            await client.send_message(config.OWNER_ID, f"📊 {message}")
        except Exception as e:
            print(f"Logging error: {e}")
    
    @staticmethod
    async def log_chat_added(client: Client, chat_title: str, added_by: int, chat_type: str):
        message = f"""
**New Chat Added**

**Title:** {chat_title}
**Type:** {chat_type}
**Added By:** {added_by}
"""
        await Logger.log_to_owner(client, message)
    
    @staticmethod
    async def log_request_accepted(client: Client, chat_title: str, username: str):
        message = f"✅ Request accepted in {chat_title} for @{username}"
        await Logger.log_to_owner(client, message)
    
    @staticmethod
    async def log_error(client: Client, error: str):
        message = f"❌ Error: {error}"
        await Logger.log_to_owner(client, message)
