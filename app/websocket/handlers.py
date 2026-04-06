"""
WebSocket event handlers for game communication.
"""
import json
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.websocket.manager import manager
from app.websocket.game_session import get_or_create_session, register_session, remove_session
from app.services.ai_opponent import get_ai_session, register_ai_session, remove_ai_session
from app.database import AsyncSessionLocal
from app.models.deck import Deck, DeckCard
from app.models.user import User
from app.services.matchmaking_service import MatchmakingService
from app.utils.security import decode_token


async def authenticate_websocket(websocket: WebSocket) -> tuple[int, str]:
    """
    Authenticate a WebSocket connection via query param token.
    Returns (user_id, username).
    """
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        raise WebSocketDisconnect()

    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=4001, reason="Invalid token")
            raise WebSocketDisconnect()
    except Exception:
        await websocket.close(code=4001, reason="Invalid token")
        raise WebSocketDisconnect()

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            await websocket.close(code=4001, reason="User not found")
            raise WebSocketDisconnect()

    return user_id, user.username


async def ws_game_handler(websocket: WebSocket, session_id: str):
    """Handle WebSocket connection for an active game."""
    user_id, username = await authenticate_websocket(websocket)

    # Check if this is an AI game session
    ai_handler = get_ai_session(session_id)
    if ai_handler:
        # AI game session
        handler = ai_handler
        is_ai_game = True
    else:
        # Regular PvP session
        is_ai_game = False
        mm = MatchmakingService()
        session_data = await mm.get_session(session_id)

        if not session_data:
            # Check in-memory sessions
            handler = get_or_create_session(session_id)
            if not handler:
                await websocket.close(code=4004, reason="Game session not found")
                return
        else:
            # Create new handler
            p1 = session_data["player1"]
            p2 = session_data["player2"]

            handler = get_or_create_session(session_id)
            if handler is None:
                from app.websocket.game_session import GameSessionHandler
                handler = GameSessionHandler(session_id, p1, p2)

                # Load decks
                async with AsyncSessionLocal() as db:
                    deck1_cards = await _load_deck_cards(db, p1["deck_id"])
                    deck2_cards = await _load_deck_cards(db, p2["deck_id"])

                handler.initialize_game(deck1_cards, deck2_cards)
                register_session(session_id, handler)

    # Register connection
    await manager.connect(websocket, session_id, user_id)

    # Send initial state
    state = handler.get_state_for_player(user_id)
    await websocket.send_json({
        "event": "connected",
        "session_id": session_id,
        "user_id": user_id,
        "state": state,
    })

    # For PvP, notify other player
    if not is_ai_game:
        other_id = handler.p2_id if user_id == handler.p1_id else handler.p1_id
        await manager.send_to_user(other_id, {
            "event": "opponent_joined",
            "username": username,
        })
    else:
        # For AI games, notify human player
        await websocket.send_json({
            "event": "opponent_joined",
            "username": handler.ai_username,
        })

    try:
        while True:
            data = await websocket.receive_json()
            await handle_ws_message(websocket, handler, user_id, data, is_ai_game)
    except WebSocketDisconnect:
        await manager.disconnect(session_id, user_id)
        # For PvP, notify opponent
        if not is_ai_game:
            other_id = handler.p2_id if user_id == handler.p1_id else handler.p1_id
            await manager.send_to_user(other_id, {
                "event": "opponent_disconnected",
                "user_id": user_id,
            })
    except Exception as e:
        await manager.disconnect(session_id, user_id)
        try:
            await websocket.send_json({"event": "error", "message": str(e)})
        except Exception:
            pass


async def handle_ws_message(websocket: WebSocket, handler, user_id: int, data: dict, is_ai_game: bool = False):
    """Handle incoming WebSocket messages."""
    action = data.get("action")
    payload = data.get("payload", {})

    result = await handler.process_action(user_id, action, payload)

    if "error" in result:
        await websocket.send_json({
            "event": "action_error",
            "action": action,
            "error": result["error"],
        })
        return

    # Send events back to the acting player
    await websocket.send_json({
        "event": "action_result",
        "action": action,
        "events": result.get("events", []),
    })

    # Broadcast full state update to all
    state_update = {
        "event": "state_update",
        **result.get("state", {}),
    }
    await manager.broadcast_to_session(handler.session_id, state_update)

    # For AI games: if human ended turn, trigger AI turn
    if is_ai_game and action == "end_turn" and not result.get("error"):
        asyncio.create_task(_execute_ai_turn(handler))


async def _load_deck_cards(db: AsyncSession, deck_id: int) -> list:
    """Load cards from a deck."""
    result = await db.execute(
        select(DeckCard)
        .where(DeckCard.deck_id == deck_id)
    )
    deck_cards = result.scalars().all()

    cards = []
    for dc in deck_cards:
        card = dc.card
        for _ in range(dc.quantity):
            cards.append({
                "card_id": card.id,
                "name": card.name,
                "card_type": card.card_type.value,
                "attribute": card.attribute.value if card.attribute else None,
                "hp": card.hp,
                "atk": card.atk,
                "defense": card.defense,
                "cost": card.cost,
                "rarity": card.rarity.value,
                "description": card.description,
                "passive_ability": card.passive_ability,
                "active_ability": card.active_ability,
                "effect_data": card.effect_data or {},
            })
    return cards


async def _execute_ai_turn(handler):
    """
    Execute AI turn after human ends their turn.
    This runs asynchronously so the human sees the AI "thinking".
    """
    await asyncio.sleep(0.5)  # Brief pause before AI starts

    # Send AI thinking indicator
    await manager.broadcast_to_session(handler.session_id, {
        "event": "ai_thinking",
        "ai_id": handler.ai_id,
        "difficulty": handler.difficulty.value,
    })

    # Execute AI turn
    events = await handler.execute_ai_turn()

    # Send AI turn events
    await manager.broadcast_to_session(handler.session_id, {
        "event": "ai_turn_events",
        "events": events,
    })

    # Send final state update
    state_update = handler._build_state_update()
    await manager.broadcast_to_session(handler.session_id, {
        "event": "state_update",
        **state_update,
    })
