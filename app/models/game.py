from sqlalchemy import Column, Integer, String, ForeignKey, Text, Enum, JSON
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class GamePhase(str, enum.Enum):
    WAITING = "WAITING"
    DRAW = "DRAW"
    MAIN = "MAIN"
    BATTLE = "BATTLE"
    END = "END"
    FINISHED = "FINISHED"


class GameSession(Base):
    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)

    player1_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    player2_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    winner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(20), default="WAITING")

    current_turn = Column(Integer, default=1)
    current_player_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    current_phase = Column(Enum(GamePhase), default=GamePhase.WAITING)

    player1_state = Column(JSON, default=dict)
    player2_state = Column(JSON, default=dict)

    created_at = Column(Integer, nullable=False)
    updated_at = Column(Integer, nullable=False)

    player1 = relationship("User", foreign_keys=[player1_id], back_populates="game_sessions_as_p1")
    player2 = relationship("User", foreign_keys=[player2_id], back_populates="game_sessions_as_p2")
    winner = relationship("User", foreign_keys=[winner_id])


class GamePlayerState(Base):
    __tablename__ = "game_player_states"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("game_sessions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    deck_id = Column(Integer, ForeignKey("decks.id"), nullable=False)
    state_data = Column(JSON, default=dict)

    session = relationship("GameSession")
    user = relationship("User")
    deck = relationship("Deck")


class GameCardInstance(Base):
    __tablename__ = "game_card_instances"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("game_sessions.id", ondelete="CASCADE"), nullable=False)
    card_id = Column(Integer, ForeignKey("cards.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    instance_id = Column(String(50), nullable=False)
    location = Column(String(20), default="DECK")

    hp = Column(Integer, default=0)
    atk = Column(Integer, default=0)
    defense = Column(Integer, default=0)
    is_flipped = Column(Integer, default=0)
    can_attack = Column(Integer, default=0)
    is_exhausted = Column(Integer, default=0)
    position = Column(String(20), default="DECK")
    slot_index = Column(Integer, nullable=True)

    session = relationship("GameSession")
    card = relationship("Card")
    owner = relationship("User")
