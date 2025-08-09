# app/state/session_store.py

class SessionStore:
    def __init__(self):
        self.sessions = {}  # session_id -> dict

    def get(self, session_id: str):
        return self.sessions.get(session_id, {})

    def set(self, session_id: str, data: dict):
        self.sessions[session_id] = data

    def delete(self, session_id: str):
        self.sessions.pop(session_id, None)

session_store = SessionStore()
