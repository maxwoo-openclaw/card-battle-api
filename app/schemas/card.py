from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from app.models.card import CardType, MonsterAttribute, CardRarity


class CardCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    card_type: CardType
    attribute: Optional[MonsterAttribute] = None
    hp: int = 0
    atk: int = 0
    defense: int = 0
    cost: int = 0
    rarity: CardRarity = CardRarity.COMMON
    passive_ability: Optional[str] = None
    active_ability: Optional[str] = None
    effect_data: Dict[str, Any] = {}


class CardRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    card_type: CardType
    attribute: Optional[MonsterAttribute]
    hp: int
    atk: int
    defense: int
    cost: int
    rarity: CardRarity
    is_legendary: bool
    passive_ability: Optional[str]
    active_ability: Optional[str]
    effect_data: Dict[str, Any]

    model_config = {"from_attributes": True}


class CardSearch(BaseModel):
    name: Optional[str] = None
    card_type: Optional[CardType] = None
    attribute: Optional[MonsterAttribute] = None
    rarity: Optional[CardRarity] = None
    min_cost: Optional[int] = None
    max_cost: Optional[int] = None
    min_atk: Optional[int] = None
    max_atk: Optional[int] = None
    min_hp: Optional[int] = None
    max_hp: Optional[int] = None
