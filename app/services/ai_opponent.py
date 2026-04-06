"""
AI Opponent Service for Card Battle Game.
Provides intelligent opponent behavior with different difficulty levels.
"""
import asyncio
import copy
import random
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum


class Difficulty(str, Enum):
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"


class AIOpponent:
    """
    AI opponent that makes decisions based on difficulty level.
    Easy: Random valid actions
    Normal: Value-based decisions
    Hard: Minimax-like evaluation with lookahead
    """

    def __init__(self, difficulty: Difficulty = Difficulty.NORMAL):
        self.difficulty = difficulty
        self.think_delay = 2.0 if difficulty == Difficulty.HARD else 1.5

    def evaluate_board_state(
        self, ai_state: Dict[str, Any], opponent_state: Dict[str, Any]
    ) -> float:
        """
        Evaluate the current board state from AI's perspective.
        Returns a score where positive = good for AI.
        """
        score = 0.0

        # HP advantage (weighted heavily)
        hp_diff = ai_state["hp"] - opponent_state["hp"]
        score += hp_diff * 0.1

        # Monster advantage
        ai_monsters = [m for m in ai_state["field_monsters"] if m]
        opp_monsters = [m for m in opponent_state["field_monsters"] if m]

        ai_monster_score = sum(
            m.get("current_atk", m.get("atk", 0)) + m.get("current_hp", m.get("hp", 0)) * 0.5
            for m in ai_monsters
        )
        opp_monster_score = sum(
            m.get("current_atk", m.get("atk", 0)) + m.get("current_hp", m.get("hp", 0)) * 0.5
            for m in opp_monsters
        )

        score += (ai_monster_score - opp_monster_score) * 0.5

        # Card advantage (hand size)
        score += (len(ai_state["hand"]) - len(opponent_state["hand"])) * 5

        # Deck advantage
        score += (len(ai_state["deck_cards"]) - len(opponent_state["deck_cards"])) * 2

        # Energy efficiency
        score += ai_state["energy"] * 3

        return score

    def get_playable_cards(
        self, state: Dict[str, Any]
    ) -> List[Tuple[int, Dict]]:  # (card_index, card)
        """Get all playable cards in hand with valid slots."""
        playable = []
        for i, card in enumerate(state["hand"]):
            cost = card.get("cost", 0)
            if cost > state["energy"]:
                continue

            card_type = card.get("card_type", "MONSTER")
            if card_type == "MONSTER":
                # Find empty slots
                for slot_idx, occupied in enumerate(state["field_monsters"]):
                    if occupied is None:
                        playable.append((i, card))
                        break
            else:
                # Spell/trap - find empty spell slot
                for slot_idx, occupied in enumerate(state["field_spells"]):
                    if occupied is None:
                        playable.append((i, card))
                        break
        return playable

    def select_card_to_play(
        self, ai_state: Dict[str, Any], opponent_state: Dict[str, Any]
    ) -> Optional[Tuple[int, int]]:  # (card_index, slot_index)
        """Select which card to play based on difficulty."""
        playable = self.get_playable_cards(ai_state)
        if not playable:
            return None

        if self.difficulty == Difficulty.EASY:
            # Random selection
            chosen = random.choice(playable)
            card_index, card = chosen

            # Find a valid slot
            card_type = card.get("card_type", "MONSTER")
            if card_type == "MONSTER":
                slots = [i for i, m in enumerate(ai_state["field_monsters"]) if m is None]
            else:
                slots = [i for i, s in enumerate(ai_state["field_spells"]) if s is None]

            if slots:
                return (card_index, random.choice(slots))
            return None

        elif self.difficulty == Difficulty.NORMAL:
            # Value-based selection: prefer high value cards
            def card_value(card: Dict) -> float:
                v = 0
                if card.get("card_type") == "MONSTER":
                    v = card.get("atk", 0) + card.get("hp", 0) * 0.3
                elif card.get("active_ability"):
                    v = 30  # Spells have base value
                v -= card.get("cost", 0) * 2  # Energy efficiency
                return v

            # Sort by value descending
            playable.sort(key=lambda x: card_value(x[1]), reverse=True)

            chosen = playable[0]
            card_index, card = chosen

            card_type = card.get("card_type", "MONSTER")
            if card_type == "MONSTER":
                slots = [i for i, m in enumerate(ai_state["field_monsters"]) if m is None]
            else:
                slots = [i for i, s in enumerate(ai_state["field_spells"]) if s is None]

            if slots:
                return (card_index, slots[0])
            return None

        else:  # HARD
            # Evaluate each playable card's impact
            best_move = None
            best_score = float("-inf")

            for card_index, card in playable:
                card_type = card.get("card_type", "MONSTER")
                if card_type == "MONSTER":
                    slots = [i for i, m in enumerate(ai_state["field_monsters"]) if m is None]
                else:
                    slots = [i for i, s in enumerate(ai_state["field_spells"]) if s is None]

                for slot in slots:
                    # Simulate playing this card
                    sim_ai = copy.deepcopy(ai_state)
                    sim_ai["hand"].pop(card_index)
                    sim_card = copy.deepcopy(card)
                    sim_card["instance_id"] = "sim"

                    if card_type == "MONSTER":
                        sim_ai["field_monsters"][slot] = sim_card
                    else:
                        sim_ai["field_spells"][slot] = sim_card

                    score = self.evaluate_board_state(sim_ai, opponent_state)
                    score += card.get("atk", 0) * 0.5 if card_type == "MONSTER" else 20

                    if score > best_score:
                        best_score = score
                        best_move = (card_index, slot)

            return best_move

    def select_attack_target(
        self,
        ai_state: Dict[str, Any],
        opponent_state: Dict[str, Any],
    ) -> List[Tuple[int, int, bool]]:  # [(attacker_slot, target, is_direct)]
        """
        Select attack targets for all ready monsters.
        Returns list of (attacker_slot, target_slot_or_neg1, is_direct_attack).
        """
        attacks = []
        opp_monsters = opponent_state["field_monsters"]
        has_opp_monsters = any(m for m in opp_monsters)

        for slot, monster in enumerate(ai_state["field_monsters"]):
            if not monster or not monster.get("can_attack", False):
                continue

            atk = monster.get("current_atk", monster.get("atk", 0))

            if self.difficulty == Difficulty.EASY:
                if has_opp_monsters and random.random() < 0.7:
                    # Random monster target
                    targets = [i for i, m in enumerate(opp_monsters) if m]
                    target_slot = random.choice(targets)
                    attacks.append((slot, target_slot, False))
                else:
                    # Direct attack
                    attacks.append((slot, -1, True))

            elif self.difficulty == Difficulty.NORMAL:
                if has_opp_monsters:
                    # Prioritize killing low HP monsters
                    targets = [(i, m) for i, m in enumerate(opp_monsters) if m]
                    # Can kill?
                    killable = [(i, m) for i, m in targets if atk >= m.get("current_hp", m.get("hp", 0))]
                    if killable:
                        # Attack the one with highest ATK (most threatening)
                        killable.sort(key=lambda x: x[1].get("atk", 0), reverse=True)
                        attacks.append((slot, killable[0][0], False))
                    else:
                        # Attack lowest HP or direct
                        targets.sort(key=lambda x: x[1].get("current_hp", x[1].get("hp", 0)))
                        attacks.append((slot, targets[0][0], False))
                else:
                    attacks.append((slot, -1, True))

            else:  # HARD
                if has_opp_monsters:
                    targets = [(i, m) for i, m in enumerate(opp_monsters) if m]

                    # Evaluate each possible target
                    best_target = None
                    best_value = float("-inf")

                    for t_slot, t_mon in targets:
                        t_hp = t_mon.get("current_hp", t_mon.get("hp", 0))
                        t_atk = t_mon.get("current_atk", t_mon.get("atk", 0))

                        # Can we kill it?
                        can_kill = atk >= t_hp

                        # What's the damage we take back?
                        damage_taken = t_atk

                        # Value calculation
                        value = 0
                        if can_kill:
                            value = 1000 + t_atk * 10  # Prioritize kills
                        else:
                            value = -t_hp * 0.5  # Prefer lower HP targets

                        # Don't trade if we take too much damage
                        if damage_taken > atk * 1.5 and not can_kill:
                            value -= 500

                        if value > best_value:
                            best_value = value
                            best_target = t_slot

                    if best_target is not None:
                        attacks.append((slot, best_target, False))
                    else:
                        attacks.append((slot, -1, True))
                else:
                    attacks.append((slot, -1, True))

        return attacks

    def should_end_turn(self, ai_state: Dict[str, Any]) -> bool:
        """Determine if AI should end turn."""
        if self.difficulty == Difficulty.EASY:
            return random.random() < 0.5

        # Check if there are still useful actions
        playable = self.get_playable_cards(ai_state)
        if playable:
            return False

        ready_monsters = [m for m in ai_state["field_monsters"] if m and m.get("can_attack")]
        if ready_monsters:
            return False

        return True

    async def take_turn(
        self,
        ai_state: Dict[str, Any],
        opponent_state: Dict[str, Any],
        game_handler,  # Reference to GameSessionHandler
    ) -> List[Dict]:
        """
        Execute the AI's turn.
        Returns list of events generated.
        """
        events = []
        original_state = copy.deepcopy(ai_state)

        # Think delay to simulate "thinking"
        await asyncio.sleep(self.think_delay)

        # MAIN PHASE: Play cards
        while True:
            move = self.select_card_to_play(ai_state, opponent_state)
            if not move:
                break

            card_index, slot_index = move
            card = ai_state["hand"][card_index]

            # Check energy still available
            if card.get("cost", 0) > ai_state["energy"]:
                break

            # Execute play_card through game handler
            result = await game_handler._handle_play_card_for_ai(
                card_index, slot_index, ai_state, opponent_state
            )
            events.extend(result.get("events", []))
            if result.get("error"):
                break

            await asyncio.sleep(0.5)  # Brief delay between actions

        # BATTLE PHASE: Attack
        attacks = self.select_attack_target(ai_state, opponent_state)
        for attacker_slot, target_slot, is_direct in attacks:
            await asyncio.sleep(0.5)

            # Re-check monster is still ready
            monster = ai_state["field_monsters"][attacker_slot]
            if not monster or not monster.get("can_attack"):
                continue

            result = await game_handler._handle_attack_for_ai(
                attacker_slot, target_slot, is_direct, ai_state, opponent_state
            )
            events.extend(result.get("events", []))
            if result.get("error"):
                continue

        # END TURN
        if self.should_end_turn(ai_state):
            result = await game_handler._handle_end_turn_for_ai(ai_state)
            events.extend(result.get("events", []))
            events.append({"type": "ai_turn_ended"})

        return events


class AIGameSession:
    """
    Manages an AI vs Human game session.
    Wraps the GameSessionHandler with AI player support.
    """

    def __init__(self, session_id: str, human_id: int, human_username: str,
                 difficulty: Difficulty, deck_cards: List[Dict]):
        self.session_id = session_id
        self.human_id = human_id
        self.human_username = human_username
        self.difficulty = difficulty
        self.deck_cards = deck_cards

        # AI player info (using negative ID to distinguish from real users)
        self.ai_id = -100 - hash(difficulty) % 1000
        self.ai_username = f"AI ({difficulty.value.capitalize()})"

        # Create AI deck (use same deck for simplicity)
        import random
        self.ai_deck_cards = copy.deepcopy(deck_cards)
        random.shuffle(self.ai_deck_cards)

        # Initialize AI opponent
        self.ai_opponent = AIOpponent(difficulty)

        # Game state
        self.current_turn = 1
        self.current_player_id = human_id  # Human goes first

        # Player states (using dicts like GameSessionHandler)
        self.player1_state: Dict[str, Any] = {}
        self.player2_state: Dict[str, Any] = {}

        self.game_over = False
        self.winner_id: Optional[int] = None
        self._lock = asyncio.Lock()

    def initialize_game(self):
        """Initialize game with human as player 1, AI as player 2."""
        from app.services.game_logic import create_initial_player_state, start_turn

        # Human is player 1
        self.player1_state = create_initial_player_state(self.deck_cards)
        # AI is player 2
        self.player2_state = create_initial_player_state(self.ai_deck_cards)

        # Player 1 (human) starts with a turn
        self.player1_state = start_turn(self.player1_state)
        self.current_player_id = self.human_id

    def get_state_for_player(self, player_id: int) -> Dict[str, Any]:
        """Get a view of the game state appropriate for the requesting player."""
        is_human = player_id == self.human_id

        if is_human:
            own = copy.deepcopy(self.player1_state)
            opp = self._mask_opponent_state(self.player2_state)
        else:
            own = copy.deepcopy(self.player2_state)
            opp = self._mask_opponent_state(self.player1_state)

        return {
            "session_id": self.session_id,
            "current_turn": self.current_turn,
            "current_player_id": self.current_player_id,
            "is_your_turn": player_id == self.current_player_id,
            "your_state": own,
            "opponent_state": opp,
            "game_over": self.game_over,
            "winner_id": self.winner_id,
            "is_ai_game": True,
            "ai_difficulty": self.difficulty.value,
        }

    def _mask_opponent_state(self, state: Dict) -> Dict:
        """Mask sensitive information in opponent's state."""
        masked = copy.deepcopy(state)
        masked["hand"] = [{"count": len(state.get("hand", []))}]
        return masked

    def _build_state_update(self) -> Dict[str, Any]:
        """Build a full state update message."""
        return {
            "type": "state_update",
            "session_id": self.session_id,
            "current_turn": self.current_turn,
            "current_player_id": self.current_player_id,
            "p1_state": self.player1_state,
            "p2_state": self.player2_state,
            "p1_visible": self._mask_opponent_state(self.player1_state),
            "p2_visible": self._mask_opponent_state(self.player2_state),
            "game_over": self.game_over,
            "winner_id": self.winner_id,
            "is_ai_game": True,
            "ai_difficulty": self.difficulty.value,
        }

    async def process_action(self, player_id: int, action: str, payload: Dict) -> Dict[str, Any]:
        """Process a human player's action."""
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
            return {"events": events, "state": state_update}

    async def _handle_end_phase(self) -> List[Dict]:
        """Advance to next phase."""
        from app.models.game import GamePhase

        events = []
        old_phase = self.current_phase if hasattr(self, 'current_phase') else GamePhase.MAIN

        # Simple phase handling
        if old_phase == GamePhase.MAIN:
            self.current_phase = GamePhase.BATTLE
        elif old_phase == GamePhase.BATTLE:
            self.current_phase = GamePhase.END
        else:
            return await self._handle_end_turn()

        events.append({
            "type": "phase_change",
            "from": old_phase.value if hasattr(old_phase, 'value') else str(old_phase),
            "to": self.current_phase.value if hasattr(self.current_phase, 'value') else str(self.current_phase),
            "player_id": self.current_player_id,
        })
        return events

    async def _handle_end_turn(self) -> List[Dict]:
        """End current player's turn and start opponent's."""
        from app.services.game_logic import end_turn, start_turn, check_win_condition
        from app.models.game import GamePhase

        events = []

        # End current turn
        if self.current_player_id == self.human_id:
            self.player1_state = end_turn(self.player1_state)
        else:
            self.player2_state = end_turn(self.player2_state)

        # Switch player
        self.current_player_id = self.ai_id if self.current_player_id == self.human_id else self.human_id

        # Check if new turn
        if self.current_player_id == self.human_id:
            self.current_turn += 1

        # Start new turn
        if self.current_player_id == self.human_id:
            self.player1_state = start_turn(self.player1_state)
            self.current_phase = GamePhase.MAIN
        else:
            self.player2_state = start_turn(self.player2_state)
            self.current_phase = GamePhase.MAIN

        events.append({
            "type": "turn_change",
            "turn": self.current_turn,
            "player_id": self.current_player_id,
            "phase": self.current_phase.value,
        })

        return events

    async def _handle_play_card(self, player_id: int, payload: Dict) -> List[Dict]:
        """Handle playing a card from hand."""
        from app.services.game_logic import play_card
        from app.models.game import GamePhase

        card_index = payload.get("card_index")
        slot_index = payload.get("slot_index")

        if self.current_phase not in (GamePhase.MAIN,) and not hasattr(self, 'current_phase'):
            self.current_phase = GamePhase.MAIN

        if player_id == self.human_id:
            state = self.player1_state
            opp_state = self.player2_state
        else:
            state = self.player2_state
            opp_state = self.player1_state

        if card_index < 0 or card_index >= len(state["hand"]):
            return [{"error": "Invalid card index"}]

        card = state["hand"][card_index]

        # Check energy
        cost = card.get("cost", 0)
        if cost > state["energy"]:
            return [{"error": f"Not enough energy (need {cost}, have {state['energy']})"}]

        # Play the card
        state["hand"].pop(card_index)
        new_state, new_opp_state, events = play_card(
            state, card, slot_index, opponent_state=opp_state
        )

        if player_id == self.human_id:
            self.player1_state = new_state
            self.player2_state = new_opp_state
        else:
            self.player2_state = new_state
            self.player1_state = new_opp_state

        return events

    async def _handle_attack(self, player_id: int, payload: Dict) -> List[Dict]:
        """Handle a monster attacking."""
        from app.services.game_logic import resolve_attack, check_win_condition
        from app.models.game import GamePhase

        attacker_slot = payload.get("attacker_slot")
        defender_slot = payload.get("defender_slot")
        direct = payload.get("direct", False)

        if player_id == self.human_id:
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
            new_attacker_state, new_defender_state, events = resolve_attack(
                attacker_state, defender_state, attacker_slot, -1, defender_is_player=True
            )
        else:
            new_attacker_state, new_defender_state, events = resolve_attack(
                attacker_state, defender_state, attacker_slot, defender_slot
            )

        if player_id == self.human_id:
            self.player1_state = new_attacker_state
            self.player2_state = new_defender_state
        else:
            self.player2_state = new_attacker_state
            self.player1_state = new_defender_state

        # Check win condition
        winner = check_win_condition(self.player1_state, self.player2_state)
        if winner:
            self.game_over = True
            self.winner_id = self.human_id if winner == 1 else self.ai_id
            events.append({
                "type": "game_over",
                "winner_id": self.winner_id,
                "reason": "HP reached 0",
            })

        return events

    async def _handle_surrender(self, player_id: int) -> List[Dict]:
        """Handle a player surrendering."""
        self.game_over = True
        self.winner_id = self.ai_id if player_id == self.human_id else self.human_id
        return [{
            "type": "game_over",
            "winner_id": self.winner_id,
            "reason": "surrender",
            "loser_id": player_id,
        }]

    # AI-specific handlers (used by AI opponent)
    async def _handle_play_card_for_ai(
        self, card_index: int, slot_index: int,
        ai_state: Dict, opp_state: Dict
    ) -> Dict:
        """Handle AI playing a card."""
        from app.services.game_logic import play_card

        if card_index < 0 or card_index >= len(ai_state["hand"]):
            return {"error": "Invalid card index"}

        card = ai_state["hand"][card_index]
        cost = card.get("cost", 0)
        if cost > ai_state["energy"]:
            return {"error": "Not enough energy"}

        ai_state["hand"].pop(card_index)
        new_ai_state, new_opp_state, events = play_card(
            ai_state, card, slot_index, opponent_state=opp_state
        )

        # Update state (ai_state is already self.player2_state)
        if self.current_player_id == self.ai_id:
            self.player2_state = new_ai_state
            self.player1_state = new_opp_state
        else:
            self.player1_state = new_ai_state
            self.player2_state = new_opp_state

        return {"events": events}

    async def _handle_attack_for_ai(
        self, attacker_slot: int, target_slot: int, is_direct: bool,
        ai_state: Dict, opp_state: Dict
    ) -> Dict:
        """Handle AI attacking."""
        from app.services.game_logic import resolve_attack, check_win_condition

        attacker = ai_state["field_monsters"][attacker_slot]
        if not attacker or not attacker.get("can_attack"):
            return {"error": "Cannot attack"}

        if is_direct:
            new_ai, new_opp, events = resolve_attack(
                ai_state, opp_state, attacker_slot, -1, defender_is_player=True
            )
        else:
            new_ai, new_opp, events = resolve_attack(
                ai_state, opp_state, attacker_slot, target_slot
            )

        if self.current_player_id == self.ai_id:
            self.player2_state = new_ai
            self.player1_state = new_opp
        else:
            self.player1_state = new_ai
            self.player2_state = new_opp

        # Check win
        winner = check_win_condition(self.player1_state, self.player2_state)
        if winner:
            self.game_over = True
            self.winner_id = self.human_id if winner == 1 else self.ai_id
            events.append({
                "type": "game_over",
                "winner_id": self.winner_id,
                "reason": "HP reached 0",
            })

        return {"events": events}

    async def _handle_end_turn_for_ai(self, ai_state: Dict) -> Dict:
        """Handle AI ending turn."""
        from app.services.game_logic import end_turn, start_turn
        from app.models.game import GamePhase

        ai_state = end_turn(ai_state)

        # Switch player
        self.current_player_id = self.human_id

        # New turn if back to human
        self.current_turn += 1
        self.player1_state = start_turn(self.player1_state)
        self.current_phase = GamePhase.MAIN

        return {
            "events": [{
                "type": "turn_change",
                "turn": self.current_turn,
                "player_id": self.human_id,
                "phase": "MAIN",
            }]
        }

    async def execute_ai_turn(self) -> List[Dict]:
        """Execute the AI's full turn."""
        from app.models.game import GamePhase

        self.current_phase = GamePhase.MAIN
        self.current_player_id = self.ai_id

        # Notify AI is thinking
        thinking_event = {
            "type": "ai_thinking",
            "ai_id": self.ai_id,
            "difficulty": self.difficulty.value,
        }

        events = [thinking_event]

        # Take turn
        turn_events = await self.ai_opponent.take_turn(
            self.player2_state,
            self.player1_state,
            self
        )
        events.extend(turn_events)

        return events


# Global storage for AI game sessions
_ai_sessions: Dict[str, AIGameSession] = {}


def get_ai_session(session_id: str) -> Optional[AIGameSession]:
    return _ai_sessions.get(session_id)


def register_ai_session(session_id: str, session: AIGameSession):
    _ai_sessions[session_id] = session


def remove_ai_session(session_id: str):
    _ai_sessions.pop(session_id, None)
