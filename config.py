import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Bot
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    OWNER_ID = int(os.getenv("OWNER_ID", 0))
    
    # Telethon Userbot
    API_ID = int(os.getenv("API_ID", 0))
    API_HASH = os.getenv("API_HASH")
    SESSION_STRING = os.getenv("USERBOT_SESSION", "")
    
    # Database
    MONGODB_URL = os.getenv("MONGODB_URL")
    DB_NAME = "auto_req_bot"
    
    # Logging
    LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", 0))

config = Config()
