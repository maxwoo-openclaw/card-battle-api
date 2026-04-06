from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DeckCardUpdate(BaseModel):
    card_id: int
    quantity: int = Field(1, ge=1, le=3)


class DeckCreate(BaseModel):
    name: str = Field(..., max_length=100)
    cards: List[DeckCardUpdate] = Field(default_factory=list)


class DeckUpdate(BaseModel):
    name: Optional[str] = None
    cards: Optional[List[DeckCardUpdate]] = None


class DeckCardRead(BaseModel):
    card_id: int
    quantity: int
    card_name: Optional[str] = None

    model_config = {"from_attributes": True}


class DeckRead(BaseModel):
    id: int
    name: str
    owner_id: int
    is_active: int
    cards: List[DeckCardRead] = []
    created_at: int
    updated_at: int

    model_config = {"from_attributes": True}
