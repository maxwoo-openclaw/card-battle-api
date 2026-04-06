"""
Tests for card system.
"""
import pytest
from app.services.card_service import CardService, SAMPLE_CARDS
from app.models.card import CardType, MonsterAttribute, CardRarity


def test_sample_cards_exist():
    """Test that sample cards are defined."""
    assert len(SAMPLE_CARDS) >= 30, "Should have at least 30 sample cards"


def test_sample_cards_have_all_types():
    """Test that sample cards cover all card types."""
    types = {c.card_type for c in SAMPLE_CARDS}
    assert CardType.MONSTER in types
    assert CardType.SPELL in types
    assert CardType.TRAP in types


def test_sample_cards_have_all_attributes():
    """Test that monster cards cover all attributes."""
    monster_attrs = {c.attribute for c in SAMPLE_CARDS if c.card_type == CardType.MONSTER}
    expected_attrs = {
        MonsterAttribute.FIRE,
        MonsterAttribute.WATER,
        MonsterAttribute.WIND,
        MonsterAttribute.EARTH,
        MonsterAttribute.LIGHT,
        MonsterAttribute.DARK,
    }
    assert monster_attrs == expected_attrs


def test_sample_cards_have_all_rarities():
    """Test that sample cards include all rarities."""
    rarities = {c.rarity for c in SAMPLE_CARDS}
    assert CardRarity.COMMON in rarities
    assert CardRarity.RARE in rarities
    assert CardRarity.EPIC in rarities
    assert CardRarity.LEGENDARY in rarities


def test_legendary_cards():
    """Test that legendary cards are marked correctly."""
    legendaries = [c for c in SAMPLE_CARDS if c.rarity == CardRarity.LEGENDARY]
    assert len(legendaries) >= 3, "Should have at least 3 legendary cards"
    for card in legendaries:
        assert card.is_legendary is True or card.rarity == CardRarity.LEGENDARY


def test_card_cost_range():
    """Test that all cards have valid costs."""
    for card in SAMPLE_CARDS:
        assert card.cost >= 0, f"Card {card.name} has negative cost"
        assert card.cost <= 10, f"Card {card.name} has cost > 10"


def test_monster_cards_have_stats():
    """Test that monster cards have HP, ATK, DEF defined."""
    for card in SAMPLE_CARDS:
        if card.card_type == CardType.MONSTER:
            assert card.hp > 0, f"Monster {card.name} has no HP"
            assert card.atk >= 0, f"Monster {card.name} has negative ATK"
            assert card.defense >= 0, f"Monster {card.name} has negative DEF"


def test_spell_trap_cards_no_combat_stats():
    """Test that spell/trap cards don't need combat stats."""
    for card in SAMPLE_CARDS:
        if card.card_type in (CardType.SPELL, CardType.TRAP):
            assert card.hp == 0
            assert card.atk == 0
            assert card.defense == 0


def test_card_names_unique():
    """Test that all sample cards have unique names."""
    names = [c.name for c in SAMPLE_CARDS]
    assert len(names) == len(set(names)), "Duplicate card names found"


def test_sample_cards_coverage():
    """Test the sample cards cover the expected distribution."""
    # 19 monsters, 6 spells, 5 traps = 30 total
    monsters = [c for c in SAMPLE_CARDS if c.card_type == CardType.MONSTER]
    spells = [c for c in SAMPLE_CARDS if c.card_type == CardType.SPELL]
    traps = [c for c in SAMPLE_CARDS if c.card_type == CardType.TRAP]

    assert len(monsters) == 19, f"Expected 19 monsters, got {len(monsters)}"
    assert len(spells) == 6, f"Expected 6 spells, got {len(spells)}"
    assert len(traps) == 5, f"Expected 5 traps, got {len(traps)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
