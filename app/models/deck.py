from sqlalchemy import Column, Integer, String, ForeignKey, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


deck_cards = Table(
    "deck_cards",
    Base.metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("deck_id", Integer, ForeignKey("decks.id", ondelete="CASCADE"), nullable=False),
    Column("card_id", Integer, ForeignKey("cards.id", ondelete="CASCADE"), nullable=False),
    Column("quantity", Integer, default=1),
    UniqueConstraint("deck_id", "card_id", name="uq_deck_card"),
)


class Deck(Base):
    __tablename__ = "decks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_active = Column(Integer, default=0)
    created_at = Column(Integer, nullable=False)
    updated_at = Column(Integer, nullable=False)

    owner = relationship("User", back_populates="decks")
    cards = relationship("DeckCard", back_populates="deck", cascade="all, delete-orphan")


class DeckCard(Base):
    __tablename__ = "deck_cards_detail"

    id = Column(Integer, primary_key=True, index=True)
    deck_id = Column(Integer, ForeignKey("decks.id", ondelete="CASCADE"), nullable=False)
    card_id = Column(Integer, ForeignKey("cards.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, default=1)

    deck = relationship("Deck", back_populates="cards")
    card = relationship("Card")
