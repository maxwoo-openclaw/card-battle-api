from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging
from app.database import get_db
from app.services.deck_service import DeckService
from app.schemas.deck import DeckCreate, DeckRead, DeckUpdate
from app.utils.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/decks", tags=["Decks"])
logger = logging.getLogger(__name__)


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
    logger.info(f"PUT /api/decks/{deck_id} called with data: {deck_data}")
    logger.info(f"deck_data.cards = {deck_data.cards}")
    service = DeckService(db)
    result = await service.update_deck(deck_id, current_user.id, deck_data)
    logger.info(f"Returning deck with {len(result.cards)} cards")
    return result


@router.delete("/{deck_id}", status_code=204)
async def delete_deck(
    deck_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DeckService(db)
    await service.delete_deck(deck_id, current_user.id)
