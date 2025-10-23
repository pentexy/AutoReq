from pyrogram import Client
from config import config
import asyncio

class UserBotClient:
    def __init__(self):
        self.client = None
        self.is_connected = False
    
    async def start(self):
        if not config.USERBOT_SESSION:
            return False
        
        try:
            self.client = Client(
                "userbot",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_string=config.USERBOT_SESSION
            )
            
            await self.client.start()
            self.is_connected = True
            return True
        except Exception as e:
            print(f"Userbot failed to start: {e}")
            return False
    
    async def accept_chat_join_request(self, chat_id: str, user_id: int):
        if not self.is_connected:
            return False
        
        try:
            await self.client.approve_chat_join_request(chat_id, user_id)
            return True
        except Exception as e:
            print(f"Error accepting request: {e}")
            return False
    
    async def join_chat(self, invite_link: str):
        if not self.is_connected:
            return False
        
        try:
            await self.client.join_chat(invite_link)
            return True
        except Exception as e:
            print(f"Error joining chat: {e}")
            return False

# Global instance
userbot_client = UserBotClient()
