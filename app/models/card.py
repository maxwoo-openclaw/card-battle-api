from sqlalchemy import Column, Integer, String, Text, Enum, Boolean, JSON
import enum
from app.database import Base


class CardType(str, enum.Enum):
    MONSTER = "MONSTER"
    SPELL = "SPELL"
    TRAP = "TRAP"


class MonsterAttribute(str, enum.Enum):
    FIRE = "FIRE"
    WATER = "WATER"
    WIND = "WIND"
    EARTH = "EARTH"
    LIGHT = "LIGHT"
    DARK = "DARK"


class CardRarity(str, enum.Enum):
    COMMON = "COMMON"
    RARE = "RARE"
    EPIC = "EPIC"
    LEGENDARY = "LEGENDARY"


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    card_type = Column(Enum(CardType), nullable=False)
    attribute = Column(Enum(MonsterAttribute), nullable=True)

    # Monster-specific fields
    hp = Column(Integer, default=0)
    atk = Column(Integer, default=0)
    defense = Column(Integer, default=0)
    cost = Column(Integer, default=0)

    rarity = Column(Enum(CardRarity), default=CardRarity.COMMON)
    is_legendary = Column(Boolean, default=False)

    # Passive ability: stored as JSON string (card effect description)
    passive_ability = Column(Text, nullable=True)
    active_ability = Column(Text, nullable=True)

    # Card effect data as JSON
    effect_data = Column(JSON, default=dict)

    def __repr__(self):
        return f"<Card {self.name} ({self.card_type.value})>"
