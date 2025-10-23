import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    API_ID = int(os.getenv("API_ID", 0))
    API_HASH = os.getenv("API_HASH", "")
    OWNER_ID = int(os.getenv("OWNER_ID", 0))
    
    USERBOT_SESSION = os.getenv("USERBOT_SESSION", "")
    
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DB_NAME = os.getenv("DB_NAME", "auto_req_bot")
    
    LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", 0))

config = Config()
