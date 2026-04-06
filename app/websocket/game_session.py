"""
In-memory game session handler for active games.
Coordinates game state, turn management, and event broadcasting.
"""
import asyncio
import copy
import uuid
from typing import Dict, Any, Optional, List
from app.models.game import GamePhase
from app.services.game_logic import (
    create_initial_player_state,
    start_turn,
    end_turn,
    play_card,
    resolve_attack,
    check_win_condition,
    advance_phase,
    get_next_player,
)
from app.websocket.manager import manager


class GameSessionHandler:
    """
    Handles all game logic for an active game session.
    Manages turns, phases, card plays, combat, and state synchronization.
    """

    def __init__(self, session_id: str, p1_info: Dict, p2_info: Dict):
        self.session_id = session_id
        self.p1_info = p1_info
        self.p2_info = p2_info
        self.p1_id = p1_info["user_id"]
        self.p2_id = p2_info["user_id"]

        self.current_turn = 1
        self.current_player_id = self.p1_id
        self.current_phase = GamePhase.DRAW

        self.player1_state: Dict[str, Any] = {}
        self.player2_state: Dict[str, Any] = {}
        self.deck1_cards: List[Dict] = []
        self.deck2_cards: List[Dict] = []

        self.game_over = False
        self.winner_id: Optional[int] = None
        self._lock = asyncio.Lock()

    def initialize_game(self, deck1_cards: List[Dict], deck2_cards: List[Dict]):
        """Initialize game with shuffled decks."""
        self.deck1_cards = copy.deepcopy(deck1_cards)
        self.deck2_cards = copy.deepcopy(deck2_cards)

        # Shuffle decks
        import random
        random.shuffle(self.deck1_cards)
        random.shuffle(self.deck2_cards)

        self.player1_state = create_initial_player_state(self.deck1_cards)
        self.player2_state = create_initial_player_state(self.deck2_cards)

        # Player 1 starts with a turn
        self.player1_state = start_turn(self.player1_state)
        self.current_phase = GamePhase.MAIN

    def get_state_for_player(self, player_id: int) -> Dict[str, Any]:
        """Get a view of the game state appropriate for the requesting player."""
        is_p1 = player_id == self.p1_id

        if is_p1:
            own = copy.deepcopy(self.player1_state)
            opp = self._mask_opponent_state(self.player2_state)
        else:
            own = copy.deepcopy(self.player2_state)
            opp = self._mask_opponent_state(self.player1_state)

        return {
            "session_id": self.session_id,
            "current_turn": self.current_turn,
            "current_player_id": self.current_player_id,
            "current_phase": self.current_phase.value,
            "is_your_turn": player_id == self.current_player_id,
            "your_state": own,
            "opponent_state": opp,
            "game_over": self.game_over,
            "winner_id": self.winner_id,
        }

    def _mask_opponent_state(self, state: Dict) -> Dict:
        """Mask sensitive information in opponent's state (like hand)."""
        masked = copy.deepcopy(state)
        # Hide hand contents (just show count)
        masked["hand"] = [{"count": len(state.get("hand", []))}]
        return masked

    async def process_action(self, player_id: int, action: str, payload: Dict) -> Dict[str, Any]:
        """Process a player action and return events."""
        async with self._lock:
            if self.game_over:
                return {"error": "Game is over", "events": []}

            if player_id != self.current_player_id:
                return {"error": "Not your turn", "events": []}

            events = []

            if action == "end_phase":
                events = await self._handle_end_phase()
            elif action == "end_turn":
                events = await self._handle_end_turn()
            elif action == "play_card":
                events = await self._handle_play_card(player_id, payload)
            elif action == "attack":
                events = await self._handle_attack(player_id, payload)
            elif action == "surrender":
                events = await self._handle_surrender(player_id)
            else:
                return {"error": f"Unknown action: {action}", "events": []}

            # Broadcast state update
            state_update = self._build_state_update()
            await manager.broadcast_to_session(self.session_id, state_update)

            return {"events": events, "state": state_update}

    async def _handle_end_phase(self) -> List[Dict]:
        """Advance to next phase."""
        events = []
        old_phase = self.current_phase

        if self.current_phase == GamePhase.MAIN:
            self.current_phase = GamePhase.BATTLE
        elif self.current_phase == GamePhase.BATTLE:
            self.current_phase = GamePhase.END
        else:
            # DRAW or END -> go to next turn
            return await self._handle_end_turn()

        events.append({
            "type": "phase_change",
            "from": old_phase.value,
            "to": self.current_phase.value,
            "player_id": self.current_player_id,
        })
        return events

    async def _handle_end_turn(self) -> List[Dict]:
        """End current player's turn and start opponent's."""
        events = []

        # End current turn effects
        if self.current_player_id == self.p1_id:
            self.player1_state = end_turn(self.player1_state)
        else:
            self.player2_state = end_turn(self.player2_state)

        # Switch player
        self.current_player_id = get_next_player(
            self.current_player_id, self.p1_id, self.p2_id
        )

        # Check if new turn (switched back to player 1)
        if self.current_player_id == self.p1_id:
            self.current_turn += 1

        # Start new turn
        if self.current_player_id == self.p1_id:
            self.player1_state = start_turn(self.player1_state)
            # Apply passive heals
            self.player1_state = self._apply_passive_heals(self.player1_state)
        else:
            self.player2_state = start_turn(self.player2_state)
            self.player2_state = self._apply_passive_heals(self.player2_state)

        self.current_phase = GamePhase.MAIN

        events.append({
            "type": "turn_change",
            "turn": self.current_turn,
            "player_id": self.current_player_id,
            "phase": self.current_phase.value,
        })
        return events

    def _apply_passive_heals(self, state: Dict) -> Dict:
        """Apply passive healing abilities."""
        for monster in state.get("field_monsters", []):
            if monster and monster.get("heals_on_turn_start"):
                heal = monster["heals_on_turn_start"]
                state["hp"] = min(state["hp"] + heal, state["max_hp"])
        return state

    async def _handle_play_card(self, player_id: int, payload: Dict) -> List[Dict]:
        """Handle playing a card from hand."""
        card_index = payload.get("card_index")
        slot_index = payload.get("slot_index")

        if self.current_phase not in (GamePhase.MAIN,):
            return [{"error": "Can only play cards in MAIN phase"}]

        if player_id == self.p1_id:
            state = self.player1_state
            opp_state = self.player2_state
        else:
            state = self.player2_state
            opp_state = self.player1_state

        if card_index < 0 or card_index >= len(state["hand"]):
            return [{"error": "Invalid card index"}]

        card = state["hand"][card_index]

        # Check if field slot is valid
        card_type = card.get("card_type", "MONSTER")
        if card_type == "MONSTER":
            if slot_index < 0 or slot_index >= 5:
                return [{"error": "Invalid monster slot (0-4)"}]
            if state["field_monsters"][slot_index] is not None:
                return [{"error": "Monster slot occupied"}]
        else:
            if slot_index < 0 or slot_index >= 5:
                return [{"error": "Invalid spell slot (0-4)"}]

        # Check energy
        cost = card.get("cost", 0)
        if cost > state["energy"]:
            return [{"error": f"Not enough energy (need {cost}, have {state['energy']})"}]

        # Play the card
        state["hand"].pop(card_index)
        new_state, new_opp_state, events = play_card(
            state, card, slot_index, opponent_state=opp_state
        )

        if player_id == self.p1_id:
            self.player1_state = new_state
            self.player2_state = new_opp_state
        else:
            self.player2_state = new_state
            self.player1_state = new_opp_state

        return events

    async def _handle_attack(self, player_id: int, payload: Dict) -> List[Dict]:
        """Handle a monster attacking."""
        attacker_slot = payload.get("attacker_slot")
        defender_slot = payload.get("defender_slot")
        direct = payload.get("direct", False)

        if self.current_phase != GamePhase.BATTLE:
            return [{"error": "Can only attack in BATTLE phase"}]

        if player_id == self.p1_id:
            attacker_state = self.player1_state
            defender_state = self.player2_state
        else:
            attacker_state = self.player2_state
            defender_state = self.player1_state

        attacker = attacker_state["field_monsters"][attacker_slot]
        if not attacker:
            return [{"error": "No monster in attacker slot"}]
        if not attacker.get("can_attack", False):
            return [{"error": "This monster cannot attack this turn"}]

        # Resolve attack
        if direct:
            # Direct attack on player
            new_attacker_state, new_defender_state, events = resolve_attack(
                attacker_state, defender_state, attacker_slot, -1, defender_is_player=True
            )
        else:
            if defender_slot < 0 or defender_slot >= 5:
                return [{"error": "Invalid defender slot"}]
            new_attacker_state, new_defender_state, events = resolve_attack(
                attacker_state, defender_state, attacker_slot, defender_slot
            )

        if player_id == self.p1_id:
            self.player1_state = new_attacker_state
            self.player2_state = new_defender_state
        else:
            self.player2_state = new_attacker_state
            self.player1_state = new_defender_state

        # Check win condition
        winner = check_win_condition(self.player1_state, self.player2_state)
        if winner:
            self.game_over = True
            self.winner_id = self.p1_id if winner == 1 else self.p2_id
            events.append({
                "type": "game_over",
                "winner_id": self.winner_id,
                "reason": "HP reached 0",
            })

        return events

    async def _handle_surrender(self, player_id: int) -> List[Dict]:
        """Handle a player surrendering."""
        self.game_over = True
        self.winner_id = self.p2_id if player_id == self.p1_id else self.p1_id
        return [{
            "type": "game_over",
            "winner_id": self.winner_id,
            "reason": "surrender",
            "loser_id": player_id,
        }]

    def _build_state_update(self) -> Dict[str, Any]:
        """Build a full state update message."""
        return {
            "type": "state_update",
            "session_id": self.session_id,
            "current_turn": self.current_turn,
            "current_player_id": self.current_player_id,
            "current_phase": self.current_phase.value,
            "p1_state": self.player1_state,
            "p2_state": self.player2_state,
            "p1_visible": self._mask_opponent_state(self.player1_state),
            "p2_visible": self._mask_opponent_state(self.player2_state),
            "game_over": self.game_over,
            "winner_id": self.winner_id,
        }


# In-memory storage for active game session handlers
_active_sessions: Dict[str, GameSessionHandler] = {}


def get_or_create_session(session_id: str) -> Optional[GameSessionHandler]:
    return _active_sessions.get(session_id)


def register_session(session_id: str, handler: GameSessionHandler):
    _active_sessions[session_id] = handler


def remove_session(session_id: str):
    _active_sessions.pop(session_id, None)
