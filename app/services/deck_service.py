from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from app.models.deck import Deck, DeckCard
from app.models.card import Card
from app.models.user import User
from app.schemas.deck import DeckCreate, DeckUpdate, DeckCardUpdate
from app.utils.exceptions import NotFoundException, BadRequestException, ForbiddenException
from typing import List
import time


class DeckService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_decks_for_user(self, user_id: int) -> List[Deck]:
        result = await self.db.execute(
            select(Deck)
            .options(selectinload(Deck.cards).selectinload(DeckCard.card))
            .where(Deck.owner_id == user_id)
        )
        return list(result.scalars().all())

    async def get_deck_by_id(self, deck_id: int, user_id: int) -> Deck:
        result = await self.db.execute(
            select(Deck)
            .options(selectinload(Deck.cards).selectinload(DeckCard.card))
            .where(and_(Deck.id == deck_id))
        )
        deck = result.scalar_one_or_none()
        if not deck:
            raise NotFoundException("Deck not found")
        if deck.owner_id != user_id:
            raise ForbiddenException("Not your deck")
        return deck

    async def create_deck(self, user_id: int, deck_data: DeckCreate) -> Deck:
        now = int(time.time())
        deck = Deck(
            name=deck_data.name,
            owner_id=user_id,
            created_at=now,
            updated_at=now,
        )
        self.db.add(deck)
        await self.db.flush()

        for card_entry in deck_data.cards:
            await self._add_card_to_deck(deck.id, card_entry.card_id, card_entry.quantity)

        await self._validate_deck(deck)
        deck.updated_at = int(time.time())
        await self.db.commit()

        result = await self.db.execute(
            select(Deck)
            .options(selectinload(Deck.cards).selectinload(DeckCard.card))
            .where(Deck.id == deck.id)
        )
        return result.scalar_one()

    async def update_deck(self, deck_id: int, user_id: int, deck_data: DeckUpdate) -> Deck:
        deck = await self.get_deck_by_id(deck_id, user_id)

        if deck_data.name:
            deck.name = deck_data.name

        if deck_data.cards is not None:
            # Remove existing cards
            result = await self.db.execute(select(DeckCard).where(DeckCard.deck_id == deck_id))
            for dc in result.scalars().all():
                await self.db.delete(dc)

            # Add new cards
            for card_entry in deck_data.cards:
                await self._add_card_to_deck(deck.id, card_entry.card_id, card_entry.quantity)

            await self._validate_deck(deck)

        deck.updated_at = int(time.time())
        await self.db.commit()

        result = await self.db.execute(
            select(Deck)
            .options(selectinload(Deck.cards).selectinload(DeckCard.card))
            .where(Deck.id == deck_id)
        )
        return result.scalar_one()

    async def delete_deck(self, deck_id: int, user_id: int):
        deck = await self.get_deck_by_id(deck_id, user_id)
        await self.db.delete(deck)
        await self.db.commit()

    async def _add_card_to_deck(self, deck_id: int, card_id: int, quantity: int):
        # Check card exists
        result = await self.db.execute(select(Card).where(Card.id == card_id))
        if not result.scalar_one_or_none():
            raise BadRequestException(f"Card {card_id} does not exist")

        # Check max copies
        if quantity > 3:
            raise BadRequestException("Max 3 copies per card in a deck")

        # Check existing quantity
        result = await self.db.execute(
            select(DeckCard).where(
                and_(DeckCard.deck_id == deck_id, DeckCard.card_id == card_id)
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            new_qty = existing.quantity + quantity
            if new_qty > 3:
                raise BadRequestException("Max 3 copies per card in a deck")
            existing.quantity = new_qty
        else:
            dc = DeckCard(deck_id=deck_id, card_id=card_id, quantity=quantity)
            self.db.add(dc)

    async def _validate_deck(self, deck: Deck):
        """Validate deck rules: 30-60 cards, max 3 copies each."""
        result = await self.db.execute(
            select(DeckCard).options(selectinload(DeckCard.card)).where(DeckCard.deck_id == deck.id)
        )
        deck_cards = list(result.scalars().all())

        total = sum(dc.quantity for dc in deck_cards)
        if total < 30:
            raise BadRequestException(f"Deck must have at least 30 cards (currently {total})")
        if total > 60:
            raise BadRequestException(f"Deck must have at most 60 cards (currently {total})")

        return True
