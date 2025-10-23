from pymongo import MongoClient, ReturnDocument
from pymongo.errors import DuplicateKeyError
from .models import Chat, Request
from config import config
from datetime import datetime

class MongoDB:
    def __init__(self):
        self.client = MongoClient(config.MONGODB_URL)
        self.db = self.client[config.DB_NAME]
        self.chats = self.db.chats
        self.requests = self.db.requests
        
        # Create indexes
        self.chats.create_index("chat_id", unique=True)
        self.requests.create_index([("chat_id", 1), ("user_id", 1)])

    def add_chat(self, chat_data):
        try:
            chat = Chat(chat_data)
            result = self.chats.insert_one(chat.to_dict())
            return result.inserted_id
        except DuplicateKeyError:
            return None

    def get_chat(self, chat_id):
        chat_data = self.chats.find_one({"chat_id": str(chat_id)})
        return Chat(chat_data) if chat_data else None

    def get_all_chats(self):
        return [Chat(chat) for chat in self.chats.find()]

    def update_chat_stats(self, chat_id, stats_update):
        return self.chats.find_one_and_update(
            {"chat_id": str(chat_id)},
            {"$set": stats_update},
            return_document=ReturnDocument.AFTER
        )

    def add_request(self, request_data):
        request = Request(request_data)
        result = self.requests.insert_one(request.to_dict())
        return result.inserted_id

    def get_pending_requests(self, chat_id):
        pending = list(self.requests.find({
            "chat_id": str(chat_id),
            "status": "pending"
        }))
        return [Request(req) for req in pending]

    def update_request_status(self, chat_id, user_id, status):
        update_data = {"status": status}
        if status == "accepted":
            update_data["accepted_date"] = datetime.utcnow()
        
        return self.requests.update_one(
            {"chat_id": str(chat_id), "user_id": user_id},
            {"$set": update_data}
        )

    def get_chat_stats(self, chat_id):
        total = self.requests.count_documents({"chat_id": str(chat_id)})
        pending = self.requests.count_documents({
            "chat_id": str(chat_id),
            "status": "pending"
        })
        accepted = self.requests.count_documents({
            "chat_id": str(chat_id),
            "status": "accepted"
        })
        
        return {
            "total_requests": total,
            "pending_requests": pending,
            "accepted_requests": accepted
        }
