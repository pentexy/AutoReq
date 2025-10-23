from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from datetime import datetime
from config import config

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
            chat_data['added_date'] = datetime.utcnow()
            result = self.chats.insert_one(chat_data)
            return result.inserted_id
        except DuplicateKeyError:
            return None

    def get_chat(self, chat_id):
        return self.chats.find_one({"chat_id": str(chat_id)})

    def get_all_chats(self):
        return list(self.chats.find())

    def get_chats_by_type(self, chat_type):
        return list(self.chats.find({"chat_type": chat_type}))

    def update_chat_stats(self, chat_id, stats_update):
        return self.chats.update_one(
            {"chat_id": str(chat_id)},
            {"$set": stats_update}
        )

    def add_request(self, request_data):
        request_data['request_date'] = datetime.utcnow()
        result = self.requests.insert_one(request_data)
        return result.inserted_id

    def get_pending_requests(self, chat_id):
        return list(self.requests.find({
            "chat_id": str(chat_id),
            "status": "pending"
        }))

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

# Global instance
db = MongoDB()
