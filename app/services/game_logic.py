"""
Core game logic for turn-based card battles.
"""
from typing import Dict, Any, List, Optional, Tuple
from app.models.game import GamePhase
from app.models.card import CardType
import uuid
import copy


# ============================================================================
# Game State Management
# ============================================================================

def create_initial_player_state(deck_cards: List[Dict]) -> Dict[str, Any]:
    """Create initial player state with shuffled deck and starting hand."""
    state = {
        "hp": 1000,
        "max_hp": 1000,
        "energy": 0,
        "max_energy": 10,
        "hand": [],
        "field_monsters": [None] * 5,
        "field_spells": [None] * 5,
        "deck_cards": copy.deepcopy(deck_cards),
        "graveyard": [],
        "active_buffs": [],
        "active_debuffs": [],
    }
    # Draw initial 5 cards
    for _ in range(5):
        state = draw_card(state)
    return state


def draw_card(state: Dict[str, Any]) -> Dict[str, Any]:
    """Draw the top card from deck to hand."""
    if state["deck_cards"]:
        card = state["deck_cards"].pop(0)
        if len(state["hand"]) < 10:
            state["hand"].append(card)
    return state


# ============================================================================
# Turn Structure
# ============================================================================

def start_turn(state: Dict[str, Any]) -> Dict[str, Any]:
    """Begin a new turn: draw, gain energy, refresh monsters."""
    state = draw_card(state)

    # Gain energy
    state["energy"] = min(state["energy"] + 1, state["max_energy"])

    # Refresh monsters (can attack again)
    for monster in state["field_monsters"]:
        if monster:
            monster["can_attack"] = True
            monster["is_exhausted"] = False
            # Remove temporary buffs from previous turn if duration expired
            if "temp_buff_atk" in monster:
                monster["atk"] -= monster.get("temp_buff_atk", 0)
                monster.pop("temp_buff_atk", None)

    # Decrement debuff durations
    to_remove = []
    for debuff in state.get("active_debuffs", []):
        debuff["duration"] -= 1
        if debuff["duration"] <= 0:
            to_remove.append(debuff)
            # Remove debuff effect
            if debuff["type"] == "atk_debuff":
                for monster in state["field_monsters"]:
                    if monster:
                        monster["atk"] += debuff["value"]
    for d in to_remove:
        state["active_debuffs"].remove(d)

    return state


def end_turn(state: Dict[str, Any]) -> Dict[str, Any]:
    """End the current player's turn."""
    # Exhaust all monsters
    for monster in state["field_monsters"]:
        if monster:
            monster["can_attack"] = False
            monster["is_exhausted"] = True

    return state


# ============================================================================
# Playing Cards
# ============================================================================

def can_play_card(state: Dict[str, Any], card: Dict, slot_index: int) -> Tuple[bool, str]:
    """Check if a card can be played."""
    # Check energy
    if card.get("cost", 0) > state["energy"]:
        return False, "Insufficient energy"

    card_type = card.get("card_type", "MONSTER")

    if card_type == "MONSTER":
        # Check for empty monster slot
        if state["field_monsters"][slot_index] is not None:
            return False, "Monster slot is occupied"
    elif card_type in ("SPELL", "TRAP"):
        # Spells and traps go to spell slots
        if state["field_spells"][slot_index] is not None:
            return False, "Spell slot is occupied"

    return True, ""


def play_card(
    state: Dict[str, Any],
    card: Dict,
    slot_index: int,
    target: Optional[Dict] = None,
    opponent_state: Optional[Dict[str, Any]] = None,
) -> Tuple[Dict[str, Any], Dict[str, Any], List[Dict]]:
    """
    Play a card from hand to field (or activate its effect).
    Returns: (player_state, opponent_state, events)
    """
    events = []

    if card.get("cost", 0) > state["energy"]:
        raise ValueError("Insufficient energy")

    # Deduct energy
    state["energy"] -= card.get("cost", 0)

    # Remove from hand
    card_instance = card.copy()
    card_instance["instance_id"] = str(uuid.uuid4())[:8]
    card_type = card.get("card_type", "MONSTER")

    if card_type == "MONSTER":
        card_instance["current_hp"] = card.get("hp", 0)
        card_instance["current_atk"] = card.get("atk", 0)
        card_instance["current_def"] = card.get("defense", 0)
        card_instance["can_attack"] = False  # Summoning sickness
        card_instance["is_exhausted"] = True
        state["field_monsters"][slot_index] = card_instance

        events.append({
            "type": "card_played",
            "card": card_instance,
            "slot": slot_index,
            "player": "self",
        })

        # Check passive ability
        if card.get("passive_ability"):
            state, events = apply_passive_ability(
                state, card_instance, opponent_state, events
            )

    elif card_type == "SPELL":
        card_instance["slot_index"] = slot_index
        state["field_spells"][slot_index] = card_instance
        events.append({
            "type": "spell_played",
            "card": card_instance,
            "slot": slot_index,
        })

        # Activate spell effect immediately
        state, opponent_state, events = activate_spell_effect(
            state, opponent_state, card_instance, events
        )

        # Traps stay on field; spells are used up
        state["field_spells"][slot_index] = None

    elif card_type == "TRAP":
        card_instance["slot_index"] = slot_index
        card_instance["is_active"] = True
        state["field_spells"][slot_index] = card_instance
        events.append({
            "type": "trap_set",
            "card": card_instance,
            "slot": slot_index,
        })

    return state, opponent_state, events


# ============================================================================
# Card Effects
# ============================================================================

def apply_passive_ability(
    state: Dict[str, Any],
    monster: Dict,
    opponent_state: Optional[Dict[str, Any]],
    events: List[Dict],
) -> Tuple[Dict[str, Any], List[Dict]]:
    """Apply a monster's passive ability when summoned."""
    passive = monster.get("passive_ability", "")
    if not passive:
        return state, events

    # Example passives
    if "Gain +100 ATK when opponent has 5 or fewer cards" in passive:
        if opponent_state and len(opponent_state.get("hand", [])) <= 5:
            monster["atk"] += 100
            monster["temp_buff_atk"] = monster.get("temp_buff_atk", 0) + 100
            events.append({
                "type": "buff_applied",
                "monster": monster,
                "buff": "+100 ATK",
                "source": "passive",
            })

    elif "Returns to hand instead of going to graveyard" in passive:
        monster["returns_to_hand"] = True

    elif "Heals 50 HP at start of your turn" in passive:
        monster["heals_on_turn_start"] = 50

    elif "Takes 100 less damage from attacks" in passive:
        monster["damage_reduction"] = 100

    return state, events


def activate_spell_effect(
    state: Dict[str, Any],
    opponent_state: Optional[Dict[str, Any]],
    spell: Dict,
    events: List[Dict],
) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]], List[Dict]]:
    """Activate a spell card's effect."""
    effect = spell.get("active_ability", "")
    effect_data = spell.get("effect_data", {})
    events = list(events)

    if not opponent_state:
        return state, opponent_state, events

    # Damage spell
    if "Deal 400 damage" in effect and "enemy or player" in effect.lower():
        target = effect_data.get("target", "enemy_or_player")
        if target == "enemy_or_player":
            # Deal to player HP
            opponent_state["hp"] -= 400
            events.append({
                "type": "damage_dealt",
                "target": "opponent_player",
                "damage": 400,
                "source": spell["name"],
            })
            if opponent_state["hp"] <= 0:
                events.append({"type": "player_died", "player": "opponent"})

    elif "Deal 800 damage to opponent" in effect:
        opponent_state["hp"] -= 800
        events.append({
            "type": "damage_dealt",
            "target": "opponent_player",
            "damage": 800,
            "source": spell["name"],
        })
        if opponent_state["hp"] <= 0:
            events.append({"type": "player_died", "player": "opponent"})

    elif "Deal 400 damage to opponent" in effect:
        opponent_state["hp"] -= 400
        events.append({
            "type": "damage_dealt",
            "target": "opponent_player",
            "damage": 400,
            "source": spell["name"],
        })
        if opponent_state["hp"] <= 0:
            events.append({"type": "player_died", "player": "opponent"})

    elif "Deal 300 damage to all enemy monsters" in effect:
        for monster in opponent_state["field_monsters"]:
            if monster:
                monster["current_hp"] = monster.get("current_hp", monster.get("hp", 0)) - 300
                events.append({
                    "type": "monster_damaged",
                    "monster": monster,
                    "damage": 300,
                    "source": spell["name"],
                })
        opponent_state = destroy_dead_monsters(opponent_state, events)

    elif "Heal your hero" in effect or "Heal your hero for" in effect:
        heal = effect_data.get("heal", 300)
        old_hp = state["hp"]
        state["hp"] = min(state["hp"] + heal, state["max_hp"])
        actual_heal = state["hp"] - old_hp
        events.append({
            "type": "healing",
            "target": "self_player",
            "amount": actual_heal,
            "source": spell["name"],
        })

    elif "Give target monster +300 ATK" in effect:
        # This needs a target - simplified: buff first monster
        for i, monster in enumerate(state["field_monsters"]):
            if monster:
                monster["current_atk"] = monster.get("current_atk", monster.get("atk", 0)) + 300
                monster["temp_buff_atk"] = monster.get("temp_buff_atk", 0) + 300
                events.append({
                    "type": "monster_buffed",
                    "monster": monster,
                    "buff": "+300 ATK",
                    "duration": "turn",
                    "slot": i,
                })
                break

    elif "Draw 3 cards" in effect:
        for _ in range(3):
            state = draw_card(state)
        events.append({
            "type": "cards_drawn",
            "count": 3,
            "source": spell["name"],
        })

    elif "Pay 200 HP to give all your monsters +400 ATK" in effect:
        state["hp"] -= 200
        for monster in state["field_monsters"]:
            if monster:
                monster["current_atk"] = monster.get("current_atk", monster.get("atk", 0)) + 400
                monster["temp_buff_atk"] = monster.get("temp_buff_atk", 0) + 400
        events.append({
            "type": "mass_buff",
            "buff": "+400 ATK",
            "cost": "200 HP",
            "source": spell["name"],
        })

    return state, opponent_state, events


# ============================================================================
# Combat Resolution
# ============================================================================

def resolve_attack(
    attacker_state: Dict[str, Any],
    defender_state: Dict[str, Any],
    attacker_slot: int,
    defender_slot: int,
    defender_is_player: bool = False,
) -> Tuple[Dict[str, Any], Dict[str, Any], List[Dict]]:
    """
    Resolve an attack from one monster to another (or directly to player).
    Returns updated states and list of events.
    """
    events = []
    attacker = attacker_state["field_monsters"][attacker_slot]

    if not attacker:
        raise ValueError("No attacker in slot")
    if not attacker.get("can_attack", False):
        raise ValueError("Attacker cannot attack this turn")

    attacker_state = copy.deepcopy(attacker_state)
    defender_state = copy.deepcopy(defender_state)
    attacker = attacker_state["field_monsters"][attacker_slot]

    # Mark attacker as exhausted
    attacker["can_attack"] = False
    attacker["is_exhausted"] = True

    if defender_is_player:
        # Direct attack on player
        damage = attacker.get("current_atk", attacker.get("atk", 0))
        defender_state["hp"] -= damage

        events.append({
            "type": "direct_attack",
            "attacker": attacker,
            "damage": damage,
            "target": "opponent_player",
        })

        if defender_state["hp"] <= 0:
            events.append({"type": "player_died", "player": "opponent"})

    else:
        defender = defender_state["field_monsters"][defender_slot]

        if not defender:
            # Attack goes through to player if no defender
            damage = attacker.get("current_atk", attacker.get("atk", 0))
            defender_state["hp"] -= damage
            events.append({
                "type": "attack_through",
                "attacker": attacker,
                "damage": damage,
                "target": "opponent_player",
                "reason": "no defending monster",
            })
            if defender_state["hp"] <= 0:
                events.append({"type": "player_died", "player": "opponent"})
        else:
            # Monster vs Monster combat
            atk_dmg = attacker.get("current_atk", attacker.get("atk", 0))
            def_atk = defender.get("current_atk", defender.get("atk", 0))
            def_def = defender.get("current_def", defender.get("defense", 0))

            # Apply damage reduction if defender has it
            dmg_reduction = defender.get("damage_reduction", 0)
            atk_dmg -= dmg_reduction

            # Both monsters take damage
            attacker["current_hp"] = attacker.get("current_hp", attacker.get("hp", 0)) - def_atk
            defender["current_hp"] = defender.get("current_hp", defender.get("hp", 0)) - atk_dmg

            events.append({
                "type": "combat",
                "attacker": attacker,
                "defender": defender,
                "attacker_damage": atk_dmg,
                "defender_damage": def_atk,
            })

            # Check for "returns to hand" passive
            if attacker.get("returns_to_hand"):
                attacker_state["hand"].append(attacker.copy())
                attacker_state["field_monsters"][attacker_slot] = None
                events.append({"type": "monster_returned_to_hand", "monster": attacker})
            else:
                attacker_state = destroy_dead_monsters(attacker_state, events)

            if defender.get("returns_to_hand"):
                defender_state["hand"].append(defender.copy())
                defender_state["field_monsters"][defender_slot] = None
                events.append({"type": "monster_returned_to_hand", "monster": defender})
            else:
                defender_state = destroy_dead_monsters(defender_state, events)

    # Check trap effects
    attacker_state, defender_state, events = check_trap_triggers(
        attacker_state, defender_state, attacker, events
    )

    return attacker_state, defender_state, events


def destroy_dead_monsters(state: Dict[str, Any], events: List[Dict]) -> Dict[str, Any]:
    """Move dead monsters (HP <= 0) to graveyard."""
    for i, monster in enumerate(state["field_monsters"]):
        if monster:
            hp = monster.get("current_hp", monster.get("hp", 0))
            if hp <= 0:
                state["graveyard"].append(monster.copy())
                state["field_monsters"][i] = None
                events.append({
                    "type": "monster_destroyed",
                    "monster": monster,
                    "slot": i,
                })
    return state


def check_trap_triggers(
    attacker_state: Dict[str, Any],
    defender_state: Dict[str, Any],
    attacker: Dict,
    events: List[Dict],
) -> Tuple[Dict[str, Any], Dict[str, Any], List[Dict]]:
    """Check and activate trap effects."""
    for i, trap in enumerate(defender_state["field_spells"]):
        if trap and trap.get("card_type") == "TRAP" and trap.get("is_active"):
            trap_effect = trap.get("active_ability", "")

            if "counter_attack" in trap.get("effect_data", {}).get("effect", ""):
                # Trap Hole effect
                counter_damage = trap.get("effect_data", {}).get("damage", 200)
                # Find the attacker in the field
                for j, mon in enumerate(attacker_state["field_monsters"]):
                    if mon and mon.get("instance_id") == attacker.get("instance_id"):
                        mon["current_hp"] = mon.get("current_hp", mon.get("hp", 0)) - counter_damage
                        events.append({
                            "type": "trap_triggered",
                            "trap": trap,
                            "damage": counter_damage,
                            "target_monster": mon,
                        })
                attacker_state = destroy_dead_monsters(attacker_state, events)

            # Deactivate trap after triggering
            defender_state["field_spells"][i] = None

    return attacker_state, defender_state, events


# ============================================================================
# Game Flow Helpers
# ============================================================================

def check_win_condition(
    player1_state: Dict[str, Any],
    player2_state: Dict[str, Any],
) -> Optional[int]:
    """Check if game is over. Returns winner user_id or None."""
    if player1_state["hp"] <= 0:
        return 2  # Player 2 wins
    if player2_state["hp"] <= 0:
        return 1  # Player 1 wins
    return None


def get_phase_order() -> List[GamePhase]:
    return [GamePhase.DRAW, GamePhase.MAIN, GamePhase.BATTLE, GamePhase.END]


def advance_phase(current_phase: GamePhase) -> GamePhase:
    phases = get_phase_order()
    try:
        idx = phases.index(current_phase)
        return phases[(idx + 1) % len(phases)]
    except ValueError:
        return GamePhase.DRAW


def get_next_player(current_player_id: int, p1_id: int, p2_id: int) -> int:
    return p2_id if current_player_id == p1_id else p1_id
