from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio
from config import config

class UserBotClient:
    def __init__(self):
        self.client = None
        self.is_connected = False
    
    async def start(self):
        if not config.SESSION_STRING:
            print("❌ No userbot session configured")
            return False
        
        try:
            self.client = TelegramClient(
                session=StringSession(config.SESSION_STRING),
                api_id=config.API_ID,
                api_hash=config.API_HASH
            )
            
            await self.client.start()
            self.is_connected = True
            print("✅ Userbot started successfully")
            return True
        except Exception as e:
            print(f"❌ Userbot failed to start: {e}")
            return False
    
    async def accept_join_request(self, chat_id: int, user_id: int):
        if not self.is_connected:
            return False
        
        try:
            await self.client.approve_join_request(chat_id, user_id)
            return True
        except Exception as e:
            print(f"Error accepting request: {e}")
            return False

# Global instance
userbot_client = UserBotClient()
