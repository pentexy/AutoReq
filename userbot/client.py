from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.types import Channel, Chat
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
                session=config.SESSION_STRING,
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
    
    async def get_chat_info(self, chat_id: int):
        try:
            chat = await self.client.get_entity(chat_id)
            return chat
        except Exception as e:
            print(f"Error getting chat info: {e}")
            return None

# Global instance
userbot_client = UserBotClient()
