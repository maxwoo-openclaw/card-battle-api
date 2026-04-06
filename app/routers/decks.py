from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.services.deck_service import DeckService
from app.schemas.deck import DeckCreate, DeckRead, DeckUpdate
from app.utils.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/decks", tags=["Decks"])


@router.get("", response_model=List[DeckRead])
async def get_decks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DeckService(db)
    return await service.get_decks_for_user(current_user.id)


@router.post("", response_model=DeckRead, status_code=201)
async def create_deck(
    deck_data: DeckCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DeckService(db)
    deck = await service.create_deck(current_user.id, deck_data)
    return deck


@router.get("/{deck_id}", response_model=DeckRead)
async def get_deck(
    deck_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DeckService(db)
    return await service.get_deck_by_id(deck_id, current_user.id)


@router.put("/{deck_id}", response_model=DeckRead)
async def update_deck(
    deck_id: int,
    deck_data: DeckUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DeckService(db)
    return await service.update_deck(deck_id, current_user.id, deck_data)


@router.delete("/{deck_id}", status_code=204)
async def delete_deck(
    deck_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DeckService(db)
    await service.delete_deck(deck_id, current_user.id)
