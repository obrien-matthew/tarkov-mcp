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
    pass  # Placeholder - full Item definition would be extensive


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
    pass  # Would be defined elsewhere in full schema


@dataclass
class Task:
    """Quest/task information."""
    pass  # Would be defined elsewhere in full schema


@dataclass
class ContainedItem:
    """Item with quantity information."""
    pass  # Would contain item reference and count


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
    pass  # Would contain boss details


@dataclass
class MapSwitch:
    """Map switch/lever information."""
    pass


@dataclass
class BossSpawnLocation:
    """Location where boss can spawn."""
    pass


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
