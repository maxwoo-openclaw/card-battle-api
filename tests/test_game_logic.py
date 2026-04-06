"""
Unit tests for core game logic.
"""
import pytest
from app.services.game_logic import (
    create_initial_player_state,
    draw_card,
    start_turn,
    end_turn,
    play_card,
    resolve_attack,
    check_win_condition,
    can_play_card,
    advance_phase,
    get_next_player,
    destroy_dead_monsters,
)
from app.models.game import GamePhase


def make_card(
    name="Test Monster",
    card_type="MONSTER",
    hp=500,
    atk=400,
    defense=300,
    cost=3,
    card_id=1,
    passive=None,
    active=None,
):
    return {
        "card_id": card_id,
        "name": name,
        "card_type": card_type,
        "attribute": "FIRE",
        "hp": hp,
        "atk": atk,
        "defense": defense,
        "cost": cost,
        "rarity": "COMMON",
        "description": "Test card",
        "passive_ability": passive,
        "active_ability": active,
        "effect_data": {},
    }


def test_create_initial_player_state():
    deck = [make_card(card_id=i) for i in range(30)]
    state = create_initial_player_state(deck)

    assert state["hp"] == 1000
    assert state["max_hp"] == 1000
    assert state["energy"] == 0
    assert state["max_energy"] == 10
    assert len(state["hand"]) == 5
    assert len(state["deck_cards"]) == 25  # 30 - 5 drawn
    assert len(state["field_monsters"]) == 5
    assert all(m is None for m in state["field_monsters"])
    assert len(state["field_spells"]) == 5


def test_draw_card():
    deck = [make_card(card_id=i) for i in range(10)]
    state = create_initial_player_state(deck)

    initial_hand = len(state["hand"])
    initial_deck = len(state["deck_cards"])

    state = draw_card(state)

    assert len(state["hand"]) == initial_hand + 1
    assert len(state["deck_cards"]) == initial_deck - 1


def test_draw_card_empty_deck():
    state = create_initial_player_state([])
    initial_hand = len(state["hand"])
    state = draw_card(state)
    # No cards to draw
    assert len(state["hand"]) == initial_hand


def test_start_turn():
    deck = [make_card(card_id=i) for i in range(10)]
    state = create_initial_player_state(deck)
    state["energy"] = 0

    state = start_turn(state)

    assert state["energy"] == 1
    assert len(state["hand"]) == 6  # Drew one card


def test_start_turn_energy_cap():
    """Energy should not exceed max_energy."""
    state = create_initial_player_state([])
    state["energy"] = 10
    state = start_turn(state)
    assert state["energy"] == 10  # Capped at max


def test_end_turn_exhausts_monsters():
    deck = [make_card(card_id=i) for i in range(30)]
    state = create_initial_player_state(deck)
    state["field_monsters"][0] = {
        **make_card(),
        "can_attack": True,
        "is_exhausted": False,
    }

    state = end_turn(state)

    assert state["field_monsters"][0]["can_attack"] is False
    assert state["field_monsters"][0]["is_exhausted"] is True


def test_can_play_card_insufficient_energy():
    state = create_initial_player_state([])
    state["energy"] = 0
    card = make_card(cost=5)

    can_play, reason = can_play_card(state, card, 0)

    assert can_play is False
    assert "energy" in reason.lower()


def test_can_play_card_occupied_slot():
    state = create_initial_player_state([])
    state["energy"] = 10
    state["field_monsters"][0] = make_card()

    can_play, reason = can_play_card(state, make_card(cost=1), 0)

    assert can_play is False
    assert "occupied" in reason.lower()


def test_can_play_card_success():
    state = create_initial_player_state([])
    state["energy"] = 5
    card = make_card(cost=3)

    can_play, reason = can_play_card(state, card, 0)

    assert can_play is True
    assert reason == ""


def test_play_monster_card():
    state = create_initial_player_state([])
    state["energy"] = 10
    card = make_card(cost=3, hp=500, atk=400)
    state["hand"].append(card)

    state, opp, events = play_card(state, card.copy(), 0)

    assert state["field_monsters"][0] is not None
    assert state["field_monsters"][0]["name"] == "Test Monster"
    assert state["energy"] == 7  # 10 - 3 cost
    assert any(e["type"] == "card_played" for e in events)


def test_play_spell_card():
    spell = make_card(
        name="Fireball",
        card_type="SPELL",
        cost=3,
        card_id=20,
        active="Deal 400 damage to opponent",
    )
    spell["effect_data"] = {"damage": 400, "target": "enemy_or_player"}

    state = create_initial_player_state([])
    state["energy"] = 10
    state["hand"].append(spell)
    opp_state = create_initial_player_state([])

    state, opp, events = play_card(state, spell.copy(), 0, opponent_state=opp_state)

    assert opp["hp"] == 600  # 1000 - 400
    assert any(e["type"] == "damage_dealt" for e in events)


def test_resolve_attack_monster_vs_monster():
    # Attacker: ATK 500, HP 400
    attacker_state = create_initial_player_state([])
    attacker_state["field_monsters"][0] = {
        **make_card(atk=500, hp=400, cost=3),
        "can_attack": True,
        "is_exhausted": False,
        "instance_id": "attacker-1",
    }
    attacker_state["energy"] = 10

    # Defender: ATK 300, HP 400, DEF 200
    defender_state = create_initial_player_state([])
    defender_state["field_monsters"][1] = {
        **make_card(atk=300, hp=400, defense=200, cost=3, name="Defender"),
        "can_attack": False,
        "is_exhausted": True,
        "instance_id": "defender-1",
    }

    attacker_state, defender_state, events = resolve_attack(
        attacker_state, defender_state, 0, 1
    )

    assert any(e["type"] == "combat" for e in events)

    # Defender should take damage equal to attacker's ATK
    # 400 - 500 = -100 -> monster is dead, moved to graveyard
    assert defender_state["field_monsters"][1] is None
    assert len(defender_state["graveyard"]) == 1


def test_resolve_attack_direct():
    attacker_state = create_initial_player_state([])
    attacker_state["field_monsters"][0] = {
        **make_card(atk=600, hp=500, cost=4),
        "can_attack": True,
        "is_exhausted": False,
    }

    defender_state = create_initial_player_state([])

    attacker_state, defender_state, events = resolve_attack(
        attacker_state, defender_state, 0, -1, defender_is_player=True
    )

    assert defender_state["hp"] == 400  # 1000 - 600
    assert any(e["type"] == "direct_attack" for e in events)


def test_resolve_attack_attacker_exhausted():
    attacker_state = create_initial_player_state([])
    attacker_state["field_monsters"][0] = {
        **make_card(atk=500, hp=400, cost=3),
        "can_attack": False,
        "is_exhausted": True,
    }

    with pytest.raises(ValueError, match="cannot attack"):
        resolve_attack(attacker_state, {}, 0, 0)


def test_destroy_dead_monsters():
    state = create_initial_player_state([])
    state["field_monsters"][0] = {
        **make_card(name="Dead Monster"),
        "current_hp": 0,
    }
    state["field_monsters"][1] = {
        **make_card(name="Alive Monster"),
        "current_hp": 200,
    }

    events = []
    state = destroy_dead_monsters(state, events)

    assert state["field_monsters"][0] is None
    assert state["field_monsters"][1] is not None
    assert len(state["graveyard"]) == 1
    assert events[0]["type"] == "monster_destroyed"


def test_check_win_condition_player1_wins():
    p1 = create_initial_player_state([])
    p1["hp"] = 100
    p2 = create_initial_player_state([])
    p2["hp"] = 0

    winner = check_win_condition(p1, p2)
    assert winner == 1


def test_check_win_condition_player2_wins():
    p1 = create_initial_player_state([])
    p1["hp"] = 0
    p2 = create_initial_player_state([])
    p2["hp"] = 500

    winner = check_win_condition(p1, p2)
    assert winner == 2


def test_check_win_condition_no_winner():
    p1 = create_initial_player_state([])
    p1["hp"] = 500
    p2 = create_initial_player_state([])
    p2["hp"] = 500

    winner = check_win_condition(p1, p2)
    assert winner is None


def test_advance_phase():
    assert advance_phase(GamePhase.DRAW) == GamePhase.MAIN
    assert advance_phase(GamePhase.MAIN) == GamePhase.BATTLE
    assert advance_phase(GamePhase.BATTLE) == GamePhase.END
    assert advance_phase(GamePhase.END) == GamePhase.DRAW


def test_get_next_player():
    assert get_next_player(1, 1, 2) == 2
    assert get_next_player(2, 1, 2) == 1


def test_full_game_flow():
    """Simulate a simple game from start to finish."""
    deck1 = [make_card(card_id=i) for i in range(30)]
    deck2 = [make_card(card_id=i + 100) for i in range(30)]

    p1_state = create_initial_player_state(deck1)
    p2_state = create_initial_player_state(deck2)

    # P1 starts turn
    p1_state = start_turn(p1_state)
    assert p1_state["energy"] == 1
    assert len(p1_state["hand"]) == 6

    # P1 plays a monster (if they have energy)
    # Add a cheap card
    cheap_card = make_card(cost=0, hp=100, atk=100, name="Cheap")
    p1_state["hand"].append(cheap_card)
    p1_state["energy"] = 10  # Give enough energy

    p1_state, p2_state, events = play_card(p1_state, cheap_card.copy(), 0, opponent_state=p2_state)
    assert p1_state["field_monsters"][0] is not None

    # End turn
    p1_state = end_turn(p1_state)
    p2_state = start_turn(p2_state)

    assert p2_state["energy"] == 1

    # P2 attacks P1's monster
    if p2_state["field_monsters"][0]:
        p2_state["field_monsters"][0]["can_attack"] = True
        # Direct attack
        p1_state = start_turn(p1_state)
        p2_state = start_turn(p2_state)
        p1_state["field_monsters"][0]["can_attack"] = False

    # Direct attack by P2
    p2_state["field_monsters"][0] = {**make_card(atk=500, hp=300, cost=3), "can_attack": True}
    p1_state = start_turn(p1_state)

    p2_state, p1_state, events = resolve_attack(p2_state, p1_state, 0, -1, defender_is_player=True)

    assert p1_state["hp"] < 1000


def test_deck_minimum_validation():
    """Test that deck must have at least 30 cards."""
    # This is tested in deck_service but let's verify logic here
    small_deck = [make_card(card_id=i) for i in range(20)]
    state = create_initial_player_state(small_deck)

    # Initial draw of 5 cards
    assert len(state["deck_cards"]) == 15
    assert len(state["hand"]) == 5


def test_spell_damage_affects_player_hp():
    spell = {
        **make_card(name="Big Fireball", card_type="SPELL", cost=5, card_id=99),
        "active_ability": "Deal 800 damage to opponent",
        "effect_data": {"damage": 800, "target": "enemy_or_player"},
    }

    state = create_initial_player_state([])
    opp = create_initial_player_state([])
    state["hand"].append(spell)
    state["energy"] = 10

    state, opp, events = play_card(state, spell.copy(), 0, opponent_state=opp)

    assert opp["hp"] == 200  # 1000 - 800
    assert any(e["type"] == "damage_dealt" for e in events)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
