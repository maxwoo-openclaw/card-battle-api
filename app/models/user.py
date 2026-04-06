from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    draws = Column(Integer, default=0)
    rating = Column(Float, default=1000.0)

    decks = relationship("Deck", back_populates="owner", cascade="all, delete-orphan")
    game_sessions_as_p1 = relationship("GameSession", foreign_keys="GameSession.player1_id", back_populates="player1")
    game_sessions_as_p2 = relationship("GameSession", foreign_keys="GameSession.player2_id", back_populates="player2")
