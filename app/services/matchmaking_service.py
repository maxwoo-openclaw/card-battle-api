import asyncio
import uuid
from typing import Dict, Optional, List
import time


class MatchmakingService:
    """
    Manages matchmaking queue using in-memory storage.
    Players join a queue, and when two are matched, a game session is created.
    """

    def __init__(self):
        self._local_queue: List[Dict] = []  # Queue of players waiting
        self._match_lock = asyncio.Lock()
        self._matched_sessions: Dict[str, Dict] = {}
        self._player_info: Dict[int, Dict] = {}  # user_id -> player info

    async def join_queue(self, user_id: int, username: str, deck_id: int) -> Dict:
        """Add a player to the matchmaking queue."""
        player_info = {
            "user_id": user_id,
            "username": username,
            "deck_id": deck_id,
            "queued_at": str(uuid.uuid4()),
        }

        # Don't add duplicates
        if not any(p["user_id"] == user_id for p in self._local_queue):
            self._local_queue.append(player_info)
        self._player_info[user_id] = player_info

        return player_info

    async def leave_queue(self, user_id: int):
        """Remove a player from the matchmaking queue."""
        self._local_queue = [p for p in self._local_queue if p["user_id"] != user_id]
        self._player_info.pop(user_id, None)

    async def check_for_match(self, user_id: int) -> Optional[Dict]:
        """Check if there's a match available for the user."""
        async with self._match_lock:
            for other in self._local_queue:
                if other["user_id"] != user_id:
                    # Found a match!
                    self._local_queue = [p for p in self._local_queue if p["user_id"] != user_id]
                    self._player_info.pop(user_id, None)
                    return other
            return None

    async def create_game_session(
        self,
        player1: Dict,
        player2: Dict,
    ) -> Dict:
        """Create a new game session for matched players."""
        session_id = str(uuid.uuid4())[:12]

        session = {
            "session_id": session_id,
            "player1": player1,
            "player2": player2,
            "status": "STARTING",
        }

        self._matched_sessions[session_id] = session

        return session

    async def get_session(self, session_id: str) -> Optional[Dict]:
        """Get an active game session."""
        return self._matched_sessions.get(session_id)

    async def update_session(self, session_id: str, session_data: Dict):
        """Update session data."""
        self._matched_sessions[session_id] = session_data

    async def end_session(self, session_id: str):
        """Remove a finished game session."""
        self._matched_sessions.pop(session_id, None)

    async def is_in_queue(self, user_id: int) -> bool:
        """Check if a user is currently in the matchmaking queue."""
        return any(p["user_id"] == user_id for p in self._local_queue)

    async def get_queue_position(self, user_id: int) -> int:
        """Get the user's position in the queue (0-indexed)."""
        for i, p in enumerate(self._local_queue):
            if p["user_id"] == user_id:
                return i
        return -1