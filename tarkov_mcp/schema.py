"""
Python schema definitions for Tarkov API data structures.
Used for developing MCP (Model Context Protocol) servers.

Based on the GraphQL schema from: 
https://github.com/the-hideout/tarkov-api/blob/8f3e3a866fd83a62bf7981d613fadbcf8c92679f/schema-static.mjs
"""

from typing import Optional, List, Union
from dataclasses import dataclass
from enum import Enum


class Side(Enum):
    """Game faction or player type."""
    PMC = "PMC"
    ALL = "All"
    SCAVS = "Scavs"


class Rarity(Enum):
    """Achievement difficulty/rarity tier."""
    COMMON = "Common"
    RARE = "Rare"
    LEGENDARY = "Legendary"


class ItemSourceName(Enum):
    """Deprecated - use trader instead."""
    pass  # Values would be defined based on actual API usage


@dataclass
class Achievement:
    """In-game achievements players can earn by completing specific objectives."""
    
    id: str  # 24-character hexadecimal identifier
    name: str  # Display name (e.g., "Welcome to Tarkov", "The Kappa Path")
    description: Optional[str]  # Conditions required to unlock
    hidden: bool  # Whether achievement is hidden until unlocked
    players_completed_percent: float  # Raw percentage of players completed
    adjusted_players_completed_percent: Optional[float]  # Statistically adjusted percentage
    side: Optional[str]  # Game faction ("PMC", "All", "Scavs")
    normalized_side: Optional[str]  # Lowercase standardized side
    rarity: Optional[str]  # Difficulty tier ("Common", "Rare", "Legendary")
    normalized_rarity: Optional[str]  # Lowercase standardized rarity


@dataclass
class Item:
    """Base item type - would be defined elsewhere in full schema."""
    id: str
    name: str
    short_name: Optional[str] = None
    description: Optional[str] = None
    weight: Optional[float] = None
    base_price: Optional[int] = None
    avg24h_price: Optional[int] = None
    low24h_price: Optional[int] = None
    high24h_price: Optional[int] = None
    last_low_price: Optional[int] = None
    change_last48h: Optional[float] = None
    change_last48h_percent: Optional[float] = None
    updated: Optional[str] = None
    icon_link: Optional[str] = None
    wiki_link: Optional[str] = None
    image_link: Optional[str] = None
    grid_image_link: Optional[str] = None
    base_image_link: Optional[str] = None
    types: Optional[List[str]] = None
    category: Optional[str] = None


@dataclass
class Ammo:
    """Ammunition item with ballistic properties."""
    
    item: Item
    weight: float
    caliber: Optional[str]
    stack_max_size: int
    tracer: bool
    tracer_color: Optional[str]
    ammo_type: str
    projectile_count: Optional[int]
    damage: int
    armor_damage: int
    fragmentation_chance: float
    ricochet_chance: float
    penetration_chance: float
    penetration_power: int
    penetration_power_deviation: Optional[float]
    accuracy_modifier: Optional[float]  # Replaces deprecated accuracy
    recoil_modifier: Optional[float]  # Replaces deprecated recoil
    initial_speed: Optional[float]
    light_bleed_modifier: float
    heavy_bleed_modifier: float
    stamina_burn_per_damage: Optional[float]


@dataclass
class ArmorMaterial:
    """Material properties for armor items."""
    
    id: Optional[str]
    name: Optional[str]
    destructibility: Optional[float]
    min_repair_degradation: Optional[float]
    max_repair_degradation: Optional[float]
    explosion_destructibility: Optional[float]
    min_repair_kit_degradation: Optional[float]
    max_repair_kit_degradation: Optional[float]


@dataclass
class NumberCompare:
    """Comparison operator for numeric thresholds."""
    pass  # Would contain comparison logic


@dataclass
class AttributeThreshold:
    """Attribute requirement threshold."""
    
    name: str
    requirement: NumberCompare


@dataclass
class Trader:
    """NPC trader information."""
    id: str
    name: str
    normalized_name: Optional[str] = None
    description: Optional[str] = None
    wiki_link: Optional[str] = None
    image_link: Optional[str] = None
    levels: Optional[List[dict]] = None
    currency: Optional[dict] = None
    reset_time: Optional[str] = None


@dataclass
class Task:
    """Quest/task information."""
    id: str
    name: str
    trader: Optional[Trader] = None
    map: Optional[str] = None
    experience: Optional[int] = None
    wiki_link: Optional[str] = None
    min_player_level: Optional[int] = None
    objectives: Optional[List[dict]] = None
    start_rewards: Optional[dict] = None
    finish_rewards: Optional[dict] = None
    fail_conditions: Optional[List[dict]] = None
    task_requirements: Optional[List[dict]] = None


@dataclass
class ContainedItem:
    """Item with quantity information."""
    item: Item
    count: int
    quantity: Optional[int] = None
    attributes: Optional[List[dict]] = None


@dataclass
class PriceRequirement:
    """Deprecated - use level instead."""
    pass


@dataclass
class Barter:
    """Trading exchange with NPCs."""
    
    id: str
    trader: Trader
    level: int
    task_unlock: Optional[Task]
    required_items: List[ContainedItem]
    reward_items: List[ContainedItem]
    source: str  # Deprecated - use trader and level instead
    source_name: ItemSourceName  # Deprecated - use trader instead
    requirements: List[PriceRequirement]  # Deprecated - use level instead
    buy_limit: Optional[int]


@dataclass
class MobInfo:
    """Information about AI enemies/bosses."""
    id: str
    name: str
    normalized_name: Optional[str] = None
    health: Optional[List[dict]] = None
    equipment: Optional[List[dict]] = None
    items: Optional[List[Item]] = None
    image_portrait_link: Optional[str] = None
    image_poster_link: Optional[str] = None


@dataclass
class MapSwitch:
    """Map switch/lever information."""
    id: str
    name: str
    map: str
    position: Optional[dict] = None
    operation: Optional[str] = None


@dataclass
class BossSpawnLocation:
    """Location where boss can spawn."""
    name: str
    chance: Optional[float] = None
    position: Optional[dict] = None


@dataclass
class BossEscort:
    """Boss escort/bodyguard information."""
    
    boss: MobInfo
    description: Optional[str]  # Deprecated - use lang argument on queries


@dataclass
class BossSpawn:
    """Boss spawn configuration."""
    
    boss: MobInfo
    spawn_chance: float
    spawn_locations: List[BossSpawnLocation]
    escorts: List[BossEscort]
    spawn_time: Optional[int]
    spawn_time_random: Optional[bool]
    spawn_trigger: Optional[str]
    switch: Optional[MapSwitch]
    # Deprecated fields
    name: str  # Use boss.name instead
    normalized_name: str  # Use boss.normalized_name instead


@dataclass
class Map:
    """Game map information."""
    id: str
    name: str
    normalized_name: Optional[str] = None
    wiki: Optional[str] = None
    description: Optional[str] = None
    enemies: Optional[List[str]] = None
    raidDuration: Optional[int] = None
    players: Optional[str] = None
    bosses: Optional[List[BossSpawn]] = None
    nameId: Optional[str] = None


# Deprecated types - kept for backwards compatibility

@dataclass
class HideoutModule:
    """Deprecated - replaced with HideoutStation."""
    
    id: Optional[int]  # Deprecated
    name: Optional[str]  # Deprecated
    level: Optional[int]
    item_requirements: List[ContainedItem]
    module_requirements: List['HideoutModule']


@dataclass
class HideoutStation:
    """Hideout station/module information."""
    id: str
    name: str
    normalized_name: Optional[str] = None
    image_link: Optional[str] = None
    levels: Optional[List[dict]] = None


@dataclass
class QuestRewardReputation:
    """Deprecated - part of old Quest system."""
    
    trader: Trader
    amount: float


@dataclass
class QuestObjective:
    """Deprecated - replaced with TaskObjective."""
    
    id: Optional[str]
    type: str
    target: List[str]
    target_item: Optional[Item]
    number: Optional[int]
    location: Optional[str]


@dataclass
class QuestRequirement:
    """Deprecated - replaced with TaskRequirement."""
    
    level: Optional[int]
    quests: List[List[int]]
    prerequisite_quests: List[List['Quest']]


@dataclass
class Quest:
    """Deprecated - replaced with Task."""
    
    id: str
    requirements: Optional[QuestRequirement]
    giver: Trader
    turnin: Trader
    title: str
    wiki_link: str
    exp: int
    unlocks: List[str]
    reputation: Optional[List[QuestRewardReputation]]
    objectives: List[QuestObjective]


@dataclass
class TraderPrice:
    """Deprecated - replaced with ItemPrice."""
    
    price: int
    currency: str
    price_rub: int
    trader: Trader


@dataclass
class TraderResetTime:
    """Deprecated - replaced with Trader."""
    
    name: Optional[str]  # Use Trader.name instead
    reset_timestamp: Optional[str]  # Use Trader.reset_time instead


@dataclass
class ItemPrice:
    """Current item pricing information."""
    vendor: Trader
    price: int
    currency: str
    price_rub: int
    updated: Optional[str] = None


@dataclass
class FleaMarket:
    """Flea market listing information."""
    item: Item
    price: int
    currency: str
    price_rub: int
    updated: Optional[str] = None


# Helper functions for MCP server development

def normalize_side(side: str) -> str:
    """Convert side to lowercase normalized format."""
    return side.lower() if side else ""


def normalize_rarity(rarity: str) -> str:
    """Convert rarity to lowercase normalized format."""
    return rarity.lower() if rarity else ""


def is_deprecated_field(field_name: str) -> bool:
    """Check if a field is marked as deprecated."""
    deprecated_fields = {
        'accuracy', 'recoil', 'source', 'sourceName', 'requirements',
        'name', 'normalizedName', 'description'
    }
    return field_name in deprecated_fields


def parse_item_from_api(data: dict) -> Item:
    """Parse Item from API response data."""
    return Item(
        id=data.get('id', ''),
        name=data.get('name', ''),
        short_name=data.get('shortName'),
        description=data.get('description'),
        weight=data.get('weight'),
        base_price=data.get('basePrice'),
        avg24h_price=data.get('avg24hPrice'),
        low24h_price=data.get('low24hPrice'),
        high24h_price=data.get('high24hPrice'),
        last_low_price=data.get('lastLowPrice'),
        change_last48h=data.get('changeLast48h'),
        change_last48h_percent=data.get('changeLast48hPercent'),
        updated=data.get('updated'),
        icon_link=data.get('iconLink'),
        wiki_link=data.get('wikiLink'),
        image_link=data.get('imageLink'),
        grid_image_link=data.get('gridImageLink'),
        base_image_link=data.get('baseImageLink'),
        types=data.get('types', []),
        category=data.get('category')
    )


def parse_trader_from_api(data: dict) -> Trader:
    """Parse Trader from API response data."""
    return Trader(
        id=data.get('id', ''),
        name=data.get('name', ''),
        normalized_name=data.get('normalizedName'),
        description=data.get('description'),
        wiki_link=data.get('wikiLink'),
        image_link=data.get('imageLink'),
        levels=data.get('levels', []),
        currency=data.get('currency'),
        reset_time=data.get('resetTime')
    )


def parse_task_from_api(data: dict) -> Task:
    """Parse Task from API response data."""
    trader_data = data.get('trader', {})
    trader = parse_trader_from_api(trader_data) if trader_data else None
    
    return Task(
        id=data.get('id', ''),
        name=data.get('name', ''),
        trader=trader,
        map=data.get('map'),
        experience=data.get('experience'),
        wiki_link=data.get('wikiLink'),
        min_player_level=data.get('minPlayerLevel'),
        objectives=data.get('objectives', []),
        start_rewards=data.get('startRewards'),
        finish_rewards=data.get('finishRewards'),
        fail_conditions=data.get('failConditions', []),
        task_requirements=data.get('taskRequirements', [])
    )


def parse_map_from_api(data: dict) -> Map:
    """Parse Map from API response data."""
    return Map(
        id=data.get('id', ''),
        name=data.get('name', ''),
        normalized_name=data.get('normalizedName'),
        wiki=data.get('wiki'),
        description=data.get('description'),
        enemies=data.get('enemies', []),
        raidDuration=data.get('raidDuration'),
        players=data.get('players'),
        bosses=data.get('bosses', []),
        nameId=data.get('nameId')
    )