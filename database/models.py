from datetime import datetime
from bson import ObjectId

class Chat:
    def __init__(self, data):
        self._id = data.get('_id', ObjectId())
        self.chat_id = data['chat_id']
        self.title = data['title']
        self.chat_type = data['chat_type']
        self.invite_link = data.get('invite_link', '')
        self.added_by = data['added_by']
        self.added_date = data.get('added_date', datetime.utcnow())
        self.is_active = data.get('is_active', True)
        self.is_admin = data.get('is_admin', False)
        self.total_requests = data.get('total_requests', 0)
        self.accepted_requests = data.get('accepted_requests', 0)
        self.pending_requests = data.get('pending_requests', 0)
    
    def to_dict(self):
        return {
            'chat_id': self.chat_id,
            'title': self.title,
            'chat_type': self.chat_type,
            'invite_link': self.invite_link,
            'added_by': self.added_by,
            'added_date': self.added_date,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'total_requests': self.total_requests,
            'accepted_requests': self.accepted_requests,
            'pending_requests': self.pending_requests
        }

class Request:
    def __init__(self, data):
        self._id = data.get('_id', ObjectId())
        self.chat_id = data['chat_id']
        self.user_id = data['user_id']
        self.username = data.get('username', '')
        self.first_name = data.get('first_name', '')
        self.request_date = data.get('request_date', datetime.utcnow())
        self.status = data.get('status', 'pending')
        self.accepted_date = data.get('accepted_date')
    
    def to_dict(self):
        return {
            'chat_id': self.chat_id,
            'user_id': self.user_id,
            'username': self.username,
            'first_name': self.first_name,
            'request_date': self.request_date,
            'status': self.status,
            'accepted_date': self.accepted_date
        }
