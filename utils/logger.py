from config import config

class Logger:
    bot = None
    
    @classmethod
    def set_bot(cls, bot_instance):
        cls.bot = bot_instance
    
    @classmethod
    async def log_to_owner(cls, message: str):
        if cls.bot and config.OWNER_ID:
            try:
                await cls.bot.send_message(config.OWNER_ID, f"📊 {message}")
                print(f"✅ Log sent to owner: {message}")
            except Exception as e:
                print(f"❌ Logging error: {e}")
    
    @classmethod
    async def log_chat_added(cls, chat_title: str, added_by: int, chat_type: str):
        message = f"""
**New Chat Added**

**Title:** {chat_title}
**Type:** {chat_type}
**Added By:** {added_by}
"""
        await cls.log_to_owner(message)
    
    @classmethod
    async def log_request_accepted(cls, chat_title: str, username: str):
        message = f"✅ Request accepted in {chat_title} for {username}"
        await cls.log_to_owner(message)
    
    @classmethod
    async def log_error(cls, error: str):
        message = f"❌ Error: {error}"
        await cls.log_to_owner(message)
