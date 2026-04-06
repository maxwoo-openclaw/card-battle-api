from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from app.models.game import GamePhase


class GameCreate(BaseModel):
    deck_id: int


class PlayerStateData(BaseModel):
    hp: int = 1000
    max_hp: int = 1000
    energy: int = 0
    max_energy: int = 10
    hand: List[Dict[str, Any]] = []
    field_monsters: List[Dict[str, Any]] = []
    field_spells: List[Dict[str, Any]] = []
    deck_cards: List[Dict[str, Any]] = []
    graveyard: List[Dict[str, Any]] = []


class GameStateData(BaseModel):
    session_id: str
    phase: GamePhase = GamePhase.WAITING
    turn: int = 1
    current_player_id: int
    player1_id: int
    player2_id: int
    player1_state: PlayerStateData
    player2_state: PlayerStateData
    winner_id: Optional[int] = None
    game_over: bool = False


class GameRead(BaseModel):
    id: int
    session_id: str
    player1_id: Optional[int]
    player2_id: Optional[int]
    winner_id: Optional[int]
    status: str
    current_turn: int
    current_phase: GamePhase

    model_config = {"from_attributes": True}


class GameStateUpdate(BaseModel):
    action: str
    payload: Dict[str, Any]


class MatchmakingStatus(BaseModel):
    in_queue: bool = False
    session_id: Optional[str] = None
    opponent_name: Optional[str] = None
