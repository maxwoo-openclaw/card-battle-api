from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from app.models.card import Card, CardType, MonsterAttribute, CardRarity
from app.schemas.card import CardCreate, CardSearch
from app.utils.exceptions import NotFoundException
from typing import List, Optional


SAMPLE_CARDS = [
    # Fire Monsters
    Card(id=1, name="Flame Imp", description="A mischievous fire elemental.", card_type=CardType.MONSTER,
         attribute=MonsterAttribute.FIRE, hp=600, atk=700, defense=400, cost=3, rarity=CardRarity.COMMON,
         passive_ability=None, active_ability="Deal 100 damage to enemy"),
    Card(id=2, name="Inferno Dragon", description="A legendary dragon of pure flame.", card_type=CardType.MONSTER,
         attribute=MonsterAttribute.FIRE, hp=1200, atk=1400, defense=1000, cost=7, rarity=CardRarity.LEGENDARY,
         passive_ability="Gain +100 ATK when opponent has 5 or fewer cards in hand",
         active_ability="Deal 300 damage to all enemy monsters"),
    Card(id=3, name="Ember Sprite", description="A small but fierce fire spirit.", card_type=CardType.MONSTER,
         attribute=MonsterAttribute.FIRE, hp=400, atk=500, defense=300, cost=2, rarity=CardRarity.COMMON,
         passive_ability=None, active_ability=None),
    Card(id=4, name="Phoenix Rebirth", description="A mythical bird that rises from ashes.", card_type=CardType.MONSTER,
         attribute=MonsterAttribute.FIRE, hp=800, atk=900, defense=600, cost=5, rarity=CardRarity.EPIC,
         passive_ability="Returns to hand instead of going to graveyard when destroyed",
         active_ability="Heal self for 400 HP"),
    # Water Monsters
    Card(id=5, name="Tide Guardian", description="Protector of the deep seas.", card_type=CardType.MONSTER,
         attribute=MonsterAttribute.WATER, hp=900, atk=400, defense=800, cost=4, rarity=CardRarity.RARE,
         passive_ability=None, active_ability="Give target monster +200 DEF for 2 turns"),
    Card(id=6, name="Kraken", description="Giant sea monster of legend.", card_type=CardType.MONSTER,
         attribute=MonsterAttribute.WATER, hp=1400, atk=1100, defense=900, cost=8, rarity=CardRarity.LEGENDARY,
         passive_ability="Enemy spells cost 1 more energy",
         active_ability="Draw 2 cards"),
    Card(id=7, name="Frost Sprite", description="Ice elemental of the frozen depths.", card_type=CardType.MONSTER,
         attribute=MonsterAttribute.WATER, hp=500, atk=450, defense=550, cost=3, rarity=CardRarity.COMMON,
         passive_ability=None, active_ability="Freeze one enemy monster for 1 turn"),
    # Wind Monsters
    Card(id=8, name="Storm Hawk", description="Swift aerial predator.", card_type=CardType.MONSTER,
         attribute=MonsterAttribute.WIND, hp=600, atk=800, defense=300, cost=4, rarity=CardRarity.RARE,
         passive_ability="Can attack twice in one battle phase",
         active_ability=None),
    Card(id=9, name="Zephyr Elf", description="Ethereal being of the winds.", card_type=CardType.MONSTER,
         attribute=MonsterAttribute.WIND, hp=500, atk=600, defense=400, cost=3, rarity=CardRarity.COMMON,
         passive_ability=None, active_ability="Return one card from opponent's hand to deck"),
    Card(id=10, name="Tempest God", description="Deity of hurricanes and storms.", card_type=CardType.MONSTER,
         attribute=MonsterAttribute.WIND, hp=1000, atk=1300, defense=800, cost=7, rarity=CardRarity.EPIC,
         passive_ability="All wind monsters gain +100 ATK",
         active_ability="Deal 200 damage and draw 1 card"),
    # Earth Monsters
    Card(id=11, name="Stone Golem", description="Living rock construct.", card_type=CardType.MONSTER,
         attribute=MonsterAttribute.EARTH, hp=1200, atk=600, defense=1000, cost=5, rarity=CardRarity.RARE,
         passive_ability="Takes 100 less damage from attacks",
         active_ability=None),
    Card(id=12, name="Earth Dragon", description="Ancient guardian of mountains.", card_type=CardType.MONSTER,
         attribute=MonsterAttribute.EARTH, hp=1500, atk=1200, defense=1300, cost=8, rarity=CardRarity.LEGENDARY,
         passive_ability="Cannot be destroyed by opponent spells",
         active_ability="Deal 400 damage to opponent"),
    Card(id=13, name="Moss Slime", description="Simple but resilient blob.", card_type=CardType.MONSTER,
         attribute=MonsterAttribute.EARTH, hp=700, atk=200, defense=700, cost=2, rarity=CardRarity.COMMON,
         passive_ability="Heals 50 HP at start of your turn",
         active_ability=None),
    # Light Monsters
    Card(id=14, name="Holy Knight", description="Champion of righteousness.", card_type=CardType.MONSTER,
         attribute=MonsterAttribute.LIGHT, hp=1000, atk=900, defense=700, cost=5, rarity=CardRarity.EPIC,
         passive_ability="Dark monsters deal 100 less damage to this card",
         active_ability="Heal your hero for 300 HP"),
    Card(id=15, name="Celestial Angel", description="Divine messenger from the heavens.", card_type=CardType.MONSTER,
         attribute=MonsterAttribute.LIGHT, hp=800, atk=1000, defense=800, cost=6, rarity=CardRarity.EPIC,
         passive_ability=None, active_ability="Revive one monster from your graveyard"),
    Card(id=16, name="Radiant Spirit", description="Pure energy of light.", card_type=CardType.MONSTER,
         attribute=MonsterAttribute.LIGHT, hp=400, atk=550, defense=350, cost=2, rarity=CardRarity.COMMON,
         passive_ability=None, active_ability=None),
    # Dark Monsters
    Card(id=17, name="Shadow Knight", description="Warrior of the dark realm.", card_type=CardType.MONSTER,
         attribute=MonsterAttribute.DARK, hp=900, atk=950, defense=650, cost=5, rarity=CardRarity.EPIC,
         passive_ability="Light monsters deal 100 less damage to this card",
         active_ability="Give target monster -200 ATK for 2 turns"),
    Card(id=18, name="Demon Lord", description="Overlord of all darkness.", card_type=CardType.MONSTER,
         attribute=MonsterAttribute.DARK, hp=1600, atk=1500, defense=1000, cost=10, rarity=CardRarity.LEGENDARY,
         passive_ability="Gains +200 ATK for each dark monster in play",
         active_ability="Destroy one enemy monster"),
    Card(id=19, name="Dark Imp", description="Mischievous servant of evil.", card_type=CardType.MONSTER,
         attribute=MonsterAttribute.DARK, hp=450, atk=600, defense=350, cost=3, rarity=CardRarity.COMMON,
         passive_ability=None, active_ability=None),
    # Spells
    Card(id=20, name="Fireball", description="Hurls a ball of fire at the enemy.", card_type=CardType.SPELL,
         attribute=None, hp=0, atk=0, defense=0, cost=3, rarity=CardRarity.COMMON,
         active_ability="Deal 400 damage to one enemy or player",
         effect_data={"damage": 400, "target": "enemy_or_player"}),
    Card(id=21, name="Healing Light", description="Restorative holy magic.", card_type=CardType.SPELL,
         attribute=None, hp=0, atk=0, defense=0, cost=2, rarity=CardRarity.COMMON,
         active_ability="Heal your hero for 300 HP",
         effect_data={"heal": 300, "target": "self"}),
    Card(id=22, name="Lightning Strike", description="Calls down devastating lightning.", card_type=CardType.SPELL,
         attribute=MonsterAttribute.WIND, hp=0, atk=0, defense=0, cost=4, rarity=CardRarity.RARE,
         active_ability="Deal 300 damage to all enemy monsters",
         effect_data={"damage": 300, "target": "all_enemy_monsters"}),
    Card(id=23, name="Power Surge", description="Amplifies the energies of a monster.", card_type=CardType.SPELL,
         attribute=MonsterAttribute.LIGHT, hp=0, atk=0, defense=0, cost=2, rarity=CardRarity.COMMON,
         active_ability="Give target monster +300 ATK for this turn",
         effect_data={"buff_atk": 300, "duration": "turn", "target": "friendly_monster"}),
    Card(id=24, name="Dark Pact", description="Trade life force for power.", card_type=CardType.SPELL,
         attribute=MonsterAttribute.DARK, hp=0, atk=0, defense=0, cost=3, rarity=CardRarity.RARE,
         active_ability="Pay 200 HP to give all your monsters +400 ATK for this turn",
         effect_data={"cost_hp": 200, "buff_atk": 400, "target": "all_friendly_monsters"}),
    Card(id=25, name="Arcane Intellect", description="Draw upon ancient knowledge.", card_type=CardType.SPELL,
         attribute=MonsterAttribute.LIGHT, hp=0, atk=0, defense=0, cost=3, rarity=CardRarity.RARE,
         active_ability="Draw 3 cards",
         effect_data={"draw": 3}),
    # Traps
    Card(id=26, name="Mirror Shield", description="Reflects incoming attacks.", card_type=CardType.TRAP,
         attribute=MonsterAttribute.LIGHT, hp=0, atk=0, defense=0, cost=2, rarity=CardRarity.COMMON,
         active_ability="Negate the next attack against your hero this turn",
         effect_data={"effect": "negate_attack", "target": "hero", "duration": "turn"}),
    Card(id=27, name="Trap Hole", description="A deadly surprise for intruders.", card_type=CardType.TRAP,
         attribute=MonsterAttribute.EARTH, hp=0, atk=0, defense=0, cost=2, rarity=CardRarity.COMMON,
         active_ability="When enemy monster attacks, deal 200 damage back to them",
         effect_data={"effect": "counter_attack", "damage": 200}),
    Card(id=28, name="Time Freeze", description="Stops time itself.", card_type=CardType.TRAP,
         attribute=MonsterAttribute.WIND, hp=0, atk=0, defense=0, cost=4, rarity=CardRarity.EPIC,
         active_ability="Skip opponent's next battle phase",
         effect_data={"effect": "skip_phase", "phase": "battle"}),
    Card(id=29, name="Curse of Weakness", description="Curses enemy with frailty.", card_type=CardType.TRAP,
         attribute=MonsterAttribute.DARK, hp=0, atk=0, defense=0, cost=3, rarity=CardRarity.RARE,
         active_ability="All enemy monsters get -300 ATK for 3 turns",
         effect_data={"debuff_atk": 300, "duration": 3, "target": "all_enemy_monsters"}),
    Card(id=30, name="Divine Protection", description="Sacred barrier against harm.", card_type=CardType.TRAP,
         attribute=MonsterAttribute.LIGHT, hp=0, atk=0, defense=0, cost=3, rarity=CardRarity.EPIC,
         active_ability="Prevent all damage to your hero for the next 2 turns",
         effect_data={"effect": "damage_block", "duration": 2, "target": "hero"}),
]


class CardService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_cards(self, skip: int = 0, limit: int = 50) -> List[Card]:
        result = await self.db.execute(select(Card).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_card_by_id(self, card_id: int) -> Card:
        result = await self.db.execute(select(Card).where(Card.id == card_id))
        card = result.scalar_one_or_none()
        if not card:
            raise NotFoundException(f"Card {card_id} not found")
        return card

    async def search_cards(self, search: CardSearch) -> List[Card]:
        query = select(Card)
        conditions = []

        if search.name:
            conditions.append(Card.name.ilike(f"%{search.name}%"))
        if search.card_type:
            conditions.append(Card.card_type == search.card_type)
        if search.attribute:
            conditions.append(Card.attribute == search.attribute)
        if search.rarity:
            conditions.append(Card.rarity == search.rarity)
        if search.min_cost is not None:
            conditions.append(Card.cost >= search.min_cost)
        if search.max_cost is not None:
            conditions.append(Card.cost <= search.max_cost)
        if search.min_atk is not None:
            conditions.append(Card.atk >= search.min_atk)
        if search.max_atk is not None:
            conditions.append(Card.atk <= search.max_atk)
        if search.min_hp is not None:
            conditions.append(Card.hp >= search.min_hp)
        if search.max_hp is not None:
            conditions.append(Card.hp <= search.max_hp)

        if conditions:
            query = query.where(and_(*conditions))

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create_card(self, card_data: CardCreate) -> Card:
        card = Card(**card_data.model_dump())
        self.db.add(card)
        await self.db.commit()
        await self.db.refresh(card)
        return card

    async def seed_sample_cards(self):
        """Seed database with sample cards if none exist."""
        result = await self.db.execute(select(Card).limit(1))
        if result.scalar_one_or_none():
            return  # Already seeded

        for card in SAMPLE_CARDS:
            self.db.add(card)
        await self.db.commit()
