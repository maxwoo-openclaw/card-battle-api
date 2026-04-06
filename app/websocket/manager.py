import json
import asyncio
from typing import Dict, Set, Optional
from fastapi import WebSocket
import uuid


class ConnectionManager:
    """
    Manages WebSocket connections and message routing for game sessions.
    """

    def __init__(self):
        # session_id -> {user_id -> websocket}
        self._session_connections: Dict[str, Dict[int, WebSocket]] = {}
        # user_id -> session_id
        self._user_sessions: Dict[int, str] = {}
        # session_id -> game state
        self._active_games: Dict[str, Dict] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, session_id: str, user_id: int):
        """Accept a WebSocket connection and register it."""
        await websocket.accept()

        async with self._lock:
            if session_id not in self._session_connections:
                self._session_connections[session_id] = {}
            self._session_connections[session_id][user_id] = websocket
            self._user_sessions[user_id] = session_id

    async def disconnect(self, session_id: str, user_id: int):
        """Remove a WebSocket connection."""
        async with self._lock:
            if session_id in self._session_connections:
                self._session_connections[session_id].pop(user_id, None)
                if not self._session_connections[session_id]:
                    del self._session_connections[session_id]
            self._user_sessions.pop(user_id, None)

    async def send_to_user(self, user_id: int, message: dict):
        """Send a message to a specific user."""
        session_id = self._user_sessions.get(user_id)
        if not session_id:
            return

        async with self._lock:
            connections = self._session_connections.get(session_id, {})
            websocket = connections.get(user_id)
            if websocket:
                try:
                    await websocket.send_json(message)
                except Exception:
                    pass

    async def broadcast_to_session(self, session_id: str, message: dict, exclude_user: int = None):
        """Broadcast a message to all users in a session."""
        async with self._lock:
            connections = dict(self._session_connections.get(session_id, {}))

        for user_id, websocket in connections.items():
            if user_id != exclude_user:
                try:
                    await websocket.send_json(message)
                except Exception:
                    pass

    async def send_to_session(self, session_id: str, message: dict):
        """Send a message to all users in a session."""
        async with self._lock:
            connections = list(self._session_connections.get(session_id, {}).items())

        for user_id, websocket in connections:
            try:
                await websocket.send_json(message)
            except Exception:
                pass

    def set_game_state(self, session_id: str, state: Dict):
        """Store the current game state for a session."""
        self._active_games[session_id] = state

    def get_game_state(self, session_id: str) -> Optional[Dict]:
        """Get the current game state for a session."""
        return self._active_games.get(session_id)

    def remove_game(self, session_id: str):
        """Remove a game session."""
        self._active_games.pop(session_id, None)

    def is_user_in_session(self, user_id: int) -> bool:
        """Check if a user is in any active session."""
        return user_id in self._user_sessions

    def get_user_session(self, user_id: int) -> Optional[str]:
        """Get the session ID a user is in."""
        return self._user_sessions.get(user_id)


# Global manager instance
manager = ConnectionManager()
