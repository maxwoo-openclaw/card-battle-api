from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, join
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.user import User
from app.models.deck import Deck, DeckCard, deck_cards  # deck_cards is the Table object
from app.models.card import Card
from app.models.game import GameSession
from app.services.matchmaking_service import MatchmakingService
from app.services.deck_service import DeckService
from app.services.ai_opponent import AIGameSession, Difficulty, register_ai_session
from app.schemas.game import MatchmakingStatus, GameRead
from app.utils.security import get_current_user
import uuid

router = APIRouter(prefix="/api/matchmaking", tags=["Matchmaking"])
_matching_service: MatchmakingService | None = None


def get_matchmaking_service() -> MatchmakingService:
    global _matching_service
    if _matching_service is None:
        _matching_service = MatchmakingService()
    return _matching_service


@router.post("/queue", response_model=MatchmakingStatus)
async def join_queue(
    deck_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify deck belongs to user
    deck_service = DeckService(db)
    try:
        deck = await deck_service.get_deck_by_id(deck_id, current_user.id)
    except Exception:
        raise HTTPException(status_code=404, detail="Deck not found")

    mm = get_matchmaking_service()

    # Check if already in queue
    if await mm.is_in_queue(current_user.id):
        raise HTTPException(status_code=400, detail="Already in queue")

    # Join queue
    await mm.join_queue(current_user.id, current_user.username, deck_id)

    # Try to find a match
    match = await mm.check_for_match(current_user.id)

    if match:
        # Create game session
        session = await mm.create_game_session(
            {
                "user_id": current_user.id,
                "username": current_user.username,
                "deck_id": deck_id,
            },
            {
                "user_id": match["user_id"],
                "username": match["username"],
                "deck_id": match["deck_id"],
            },
        )

        return MatchmakingStatus(
            in_queue=False,
            session_id=session["session_id"],
            opponent_name=match["username"],
        )

    return MatchmakingStatus(in_queue=True)


@router.delete("/queue")
async def leave_queue(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    mm = get_matchmaking_service()
    await mm.leave_queue(current_user.id)
    return {"message": "Left queue"}


@router.post("/vs-ai")
async def start_vs_ai(
    deck_id: int,
    difficulty: str = Query("normal", pattern="^(easy|normal|hard)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Start a game vs AI opponent.
    difficulty: easy, normal, or hard
    """
    # Verify deck belongs to user
    deck_service = DeckService(db)
    try:
        deck = await deck_service.get_deck_by_id(deck_id, current_user.id)
    except Exception:
        raise HTTPException(status_code=404, detail="Deck not found")

    # Get deck cards - use deck_cards Table directly to avoid ORM table mismatch
    result = await db.execute(
        select(deck_cards.c.card_id, deck_cards.c.quantity, Card)
        .select_from(deck_cards.join(Card, deck_cards.c.card_id == Card.id))
        .where(deck_cards.c.deck_id == deck_id)
    )
    deck_cards_data = list(result.all())

    # Expand cards by quantity into a list
    deck_cards_list = []
    for card_id, quantity, card in deck_cards_data:
        for _ in range(quantity):
            deck_cards_list.append({
                "id": card.id,
                "name": card.name,
                "card_type": card.card_type.value if hasattr(card.card_type, 'value') else str(card.card_type),
                "hp": card.hp,
                "atk": card.atk,
                "defense": card.defense,
                "cost": card.cost,
                "passive_ability": card.passive_ability,
                "active_ability": card.active_ability,
                "effect_data": card.effect_data,
                "attribute": card.attribute.value if card.attribute else None,
            })

    # Create AI game session
    session_id = str(uuid.uuid4())[:12]
    diff = Difficulty(difficulty)

    ai_session = AIGameSession(
        session_id=session_id,
        human_id=current_user.id,
        human_username=current_user.username,
        difficulty=diff,
        deck_cards=deck_cards_list,
    )
    ai_session.initialize_game()

    # Register the session
    register_ai_session(session_id, ai_session)

    return {
        "session_id": session_id,
        "opponent_name": ai_session.ai_username,
        "difficulty": difficulty,
        "is_ai_game": True,
    }


@router.get("/status", response_model=MatchmakingStatus)
async def get_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    mm = get_matchmaking_service()

    if await mm.is_in_queue(current_user.id):
        position = await mm.get_queue_position(current_user.id)
        return MatchmakingStatus(in_queue=True)

    return MatchmakingStatus(in_queue=False)
