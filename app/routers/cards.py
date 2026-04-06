from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.database import get_db
from app.services.card_service import CardService
from app.schemas.card import CardCreate, CardRead, CardSearch
from app.models.card import CardType, MonsterAttribute, CardRarity
from app.utils.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/cards", tags=["Cards"])


@router.get("", response_model=List[CardRead])
async def get_cards(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CardService(db)
    await service.seed_sample_cards()
    return await service.get_all_cards(skip=skip, limit=limit)


@router.get("/{card_id}", response_model=CardRead)
async def get_card(
    card_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CardService(db)
    card = await service.get_card_by_id(card_id)
    return card


@router.get("/search/", response_model=List[CardRead])
async def search_cards(
    name: Optional[str] = None,
    card_type: Optional[CardType] = None,
    attribute: Optional[MonsterAttribute] = None,
    rarity: Optional[CardRarity] = None,
    min_cost: Optional[int] = None,
    max_cost: Optional[int] = None,
    min_atk: Optional[int] = None,
    max_atk: Optional[int] = None,
    min_hp: Optional[int] = None,
    max_hp: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CardService(db)
    search = CardSearch(
        name=name, card_type=card_type, attribute=attribute, rarity=rarity,
        min_cost=min_cost, max_cost=max_cost, min_atk=min_atk, max_atk=max_atk,
        min_hp=min_hp, max_hp=max_hp,
    )
    return await service.search_cards(search)


@router.post("", response_model=CardRead, status_code=201)
async def create_card(
    card_data: CardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CardService(db)
    card = await service.create_card(card_data)
    return card
