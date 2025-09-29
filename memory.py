from collections import deque, defaultdict
from typing import List, Dict
import time

class ConversationMemory:
    def __init__(self, max_messages=200):
        self.max_messages = max_messages
        self.store = defaultdict(lambda: deque(maxlen=self.max_messages))

    def add_user_message(self, session_id: str, message: str):
        self.store[session_id].append({'role': 'user', 'text': message, 'ts': int(time.time())})

    def add_bot_message(self, session_id: str, message: str):
        self.store[session_id].append({'role': 'bot', 'text': message, 'ts': int(time.time())})

    def get_context(self, session_id: str, limit: int = 10) -> List[Dict]:
        return list(self.store[session_id])[-limit:]

    def get_history(self, session_id: str) -> List[Dict]:
        return list(self.store[session_id])
