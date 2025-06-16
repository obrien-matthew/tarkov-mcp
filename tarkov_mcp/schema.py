"""
Python schema definitions for Tarkov API data structures.
Used for developing MCP (Model Context Protocol) servers.

Based on the GraphQL schema from: 
https://github.com/the-hideout/tarkov-api/blob/8f3e3a866fd83a62bf7981d613fadbcf8c92679f/schema-static.mjs
"""

from typing import Optional, List, Union, Dict, Any
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
    PRAPOR = "Prapor"
    THERAPIST = "Therapist"
    FENCE = "Fence"
    SKIER = "Skier"
    PEACEKEEPER = "Peacekeeper"
    MECHANIC = "Mechanic"
    RAGMAN = "Ragman"
    JAEGER = "Jaeger"


class ItemType(Enum):
    """Item category types."""
    AMMO = "ammo"
    ARMOR = "armor"
    BACKPACK = "backpack"
    BARTER = "barter"
    CONTAINER = "container"
    FOOD_DRINK = "foodDrink"
    GRENADE = "grenade"
    HEADPHONES = "headphones"
    HELMET = "helmet"
    INJECTORS = "injectors"
    KEYS = "keys"
    MEDS = "meds"
    MODS = "mods"
    PROVISIONS = "provisions"
    RIG = "rig"
    SUPPRESSOR = "suppressor"
    WEAPON = "weapon"


class Currency(Enum):
    """Game currencies."""
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"


class SkillName(Enum):
    """Player skills."""
    ENDURANCE = "Endurance"
    STRENGTH = "Strength"
    VITALITY = "Vitality"
    HEALTH = "Health"
    STRESS_RESISTANCE = "StressResistance"
    METABOLISM = "Metabolism"
    IMMUNITY = "Immunity"
    PERCEPTION = "Perception"
    INTELLECT = "Intellect"
    ATTENTION = "Attention"
    CHARISMA = "Charisma"
    MEMORY = "Memory"
    PISTOL = "Pistol"
    REVOLVER = "Revolver"
    SMG = "SMG"
    ASSAULT_RIFLE = "AssaultRifle"
    SHOTGUN = "Shotgun"
    SNIPER_RIFLE = "SniperRifle"
    LMG = "LMG"
    HMG = "HMG"
    LAUNCHER = "Launcher"
    THROWING = "Throwing"
    MELEE = "Melee"
    DMRS = "DMRs"


class LanguageCode(Enum):
    """Supported language codes for localization."""
    EN = "en"
    RU = "ru"
    DE = "de"
    FR = "fr"
    ES = "es"
    CS = "cs"
    HU = "hu"
    TR = "tr"
    IT = "it"
    PL = "pl"
    PT = "pt"
    SK = "sk"
    JP = "ja"
    CN = "zh"
    KO = "ko"
    NO = "no"


class GameMode(Enum):
    """Game mode types."""
    REGULAR = "regular"
    PVE = "pve"


class TraderName(Enum):
    """Standardized trader names."""
    PRAPOR = "Prapor"
    THERAPIST = "Therapist"
    FENCE = "Fence"
    SKIER = "Skier"
    PEACEKEEPER = "Peacekeeper"
    MECHANIC = "Mechanic"
    RAGMAN = "Ragman"
    JAEGER = "Jaeger"
    LIGHTKEEPER = "Lightkeeper"
    REF = "Ref"


class RequirementType(Enum):
    """Requirement types for tasks and other systems."""
    LEVEL = "level"
    SKILL = "skill"
    TASK = "task"
    TRADER = "trader"
    ITEM = "item"
    HIDEOUT_STATION = "hideoutStation"


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
class ItemSlot:
    """Item slot configuration."""
    id: str
    name: str
    name_id: Optional[str] = None
    filters: Optional[List[Dict[str, Any]]] = None
    required: Optional[bool] = None


@dataclass
class ItemProperties:
    """Base class for item-specific properties."""
    pass


@dataclass
class WeaponProperties(ItemProperties):
    """Weapon-specific properties."""
    caliber: Optional[str] = None
    default_ammo: Optional['Item'] = None
    effective_distance: Optional[int] = None
    ergonomics: Optional[int] = None
    fire_modes: Optional[List[str]] = None
    fire_rate: Optional[int] = None
    max_durability: Optional[int] = None
    default_preset: Optional['Item'] = None
    presets: Optional[List['Item']] = None
    slots: Optional[List[ItemSlot]] = None
    recoil_vertical: Optional[int] = None
    recoil_horizontal: Optional[int] = None
    center_of_impact: Optional[float] = None
    deviations: Optional[Dict[str, float]] = None
    camera_recoil: Optional[float] = None
    camera_snap: Optional[float] = None
    convergence: Optional[float] = None


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
class ArmorProperties(ItemProperties):
    """Armor-specific properties."""
    class_: Optional[int] = None
    durability: Optional[int] = None
    material: Optional[ArmorMaterial] = None
    blunt_throughput: Optional[float] = None
    zones: Optional[List[str]] = None
    armor_type: Optional[str] = None
    ergonomics_penalty: Optional[int] = None
    speed_penalty: Optional[float] = None
    turn_penalty: Optional[float] = None


@dataclass
class ContainerProperties(ItemProperties):
    """Container-specific properties."""
    capacity: Optional[int] = None
    grids: Optional[List[Dict[str, Any]]] = None


@dataclass
class FoodDrinkProperties(ItemProperties):
    """Food and drink properties."""
    energy: Optional[int] = None
    hydration: Optional[int] = None
    stim_effects: Optional[List[Dict[str, Any]]] = None


@dataclass
class GrenadeProperties(ItemProperties):
    """Grenade properties."""
    type_: Optional[str] = None
    fuse: Optional[float] = None
    min_explosion_distance: Optional[int] = None
    max_explosion_distance: Optional[int] = None
    fragments: Optional[int] = None
    contusion_radius: Optional[int] = None


@dataclass
class HelmetProperties(ItemProperties):
    """Helmet properties."""
    class_: Optional[int] = None
    durability: Optional[int] = None
    material: Optional[ArmorMaterial] = None
    blunt_throughput: Optional[float] = None
    zones: Optional[List[str]] = None
    ergonomics_penalty: Optional[int] = None
    speed_penalty: Optional[float] = None
    turn_penalty: Optional[float] = None
    deafening: Optional[str] = None
    blocks_headset: Optional[bool] = None
    slots: Optional[List[ItemSlot]] = None


@dataclass
class KeyProperties(ItemProperties):
    """Key properties."""
    uses: Optional[int] = None


@dataclass
class MedicalProperties(ItemProperties):
    """Medical item properties."""
    uses: Optional[int] = None
    use_time: Optional[int] = None
    cures: Optional[List[str]] = None


@dataclass
class StimulantsProperties(ItemProperties):
    """Stimulant properties."""
    uses: Optional[int] = None
    use_time: Optional[int] = None
    cures: Optional[List[str]] = None
    stim_effects: Optional[List[Dict[str, Any]]] = None


@dataclass
class Item:
    """Base item type with comprehensive properties."""
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
    last_offer_count: Optional[int] = None
    change_last48h: Optional[float] = None
    change_last48h_percent: Optional[float] = None
    updated: Optional[str] = None
    icon_link: Optional[str] = None
    wiki_link: Optional[str] = None
    image_link: Optional[str] = None
    grid_image_link: Optional[str] = None
    base_image_link: Optional[str] = None
    inspect_image_link: Optional[str] = None
    image_512px_link: Optional[str] = None
    image_8x_link: Optional[str] = None
    types: Optional[List[str]] = None
    category: Optional[Union[str, 'ItemCategory']] = None  # Can be string (legacy) or ItemCategory object
    categories: Optional[List['ItemCategory']] = None
    bsg_category_id: Optional[str] = None
    handbook_categories: Optional[List['HandbookCategory']] = None
    # Additional comprehensive fields
    normalized_name: Optional[str] = None
    background_color: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    grid_width: Optional[int] = None
    grid_height: Optional[int] = None
    sell_for: Optional[List['ItemPrice']] = None
    buy_for: Optional[List['ItemPrice']] = None
    contains_items: Optional[List['ContainedItem']] = None
    used_in_tasks: Optional[List['Task']] = None
    received_from_tasks: Optional[List['Task']] = None
    barters_for: Optional[List['Barter']] = None
    barters_using: Optional[List['Barter']] = None
    crafts_for: Optional[List['Craft']] = None
    crafts_using: Optional[List['Craft']] = None
    fleamarket_fee: Optional[int] = None
    properties: Optional[ItemProperties] = None
    conflicting_items: Optional[List['Item']] = None
    conflicting_slot_ids: Optional[List[str]] = None
    link: Optional[str] = None
    accuracy_modifier: Optional[float] = None
    recoil_modifier: Optional[float] = None
    ergonomics_modifier: Optional[int] = None
    has_grid: Optional[bool] = None
    blocks_headphones: Optional[bool] = None
    velocity: Optional[float] = None
    loudness: Optional[float] = None
    translation: Optional[Dict[str, str]] = None


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
class NumberCompare:
    """Comparison operator for numeric thresholds."""
    pass  # Would contain comparison logic


@dataclass
class AttributeThreshold:
    """Attribute requirement threshold."""
    
    name: str
    requirement: NumberCompare


@dataclass
class TraderLevel:
    """Trader loyalty level information."""
    level: int
    required_player_level: int
    required_reputation: float
    required_commerce: int
    pay_rate: float
    insurance_rate: Optional[float] = None
    repair_rate: Optional[float] = None
    standing: Optional[float] = None


@dataclass
class TraderCashOffer:
    """Trader cash offer information."""
    item: Item
    min_trader_level: Optional[int] = None
    price: Optional[int] = None
    currency: Optional[str] = None
    price_rub: Optional[int] = None
    updated: Optional[str] = None


@dataclass
class Trader:
    """NPC trader information."""
    id: str
    name: str
    normalized_name: Optional[str] = None
    description: Optional[str] = None
    wiki_link: Optional[str] = None
    image_link: Optional[str] = None
    levels: Optional[List[TraderLevel]] = None
    currency: Optional[Item] = None
    reset_time: Optional[str] = None
    discount: Optional[float] = None
    repair_currency: Optional[Item] = None
    insurance: Optional[Dict[str, Any]] = None
    barters: Optional[List['Barter']] = None
    cash_offers: Optional[List[TraderCashOffer]] = None


@dataclass
class TaskObjective:
    """Task objective information."""
    id: str
    type_: str
    description: str
    maps: Optional[List[str]] = None
    optional: Optional[bool] = None
    count: Optional[int] = None
    found_in_raid: Optional[bool] = None
    dog_tag_level: Optional[int] = None
    player_level_min: Optional[int] = None
    player_level_max: Optional[int] = None
    target: Optional[List[str]] = None
    target_item: Optional[Item] = None
    zones: Optional[List[Dict[str, Any]]] = None


@dataclass
class TaskRewards:
    """Task reward information."""
    experience: Optional[int] = None
    reputation: Optional[List[Dict[str, Any]]] = None
    items: Optional[List['ContainedItem']] = None
    offers: Optional[List[Dict[str, Any]]] = None
    skill_level_reward: Optional[List[Dict[str, Any]]] = None
    trader_standing: Optional[List[Dict[str, Any]]] = None
    trader_unlock: Optional[List[Trader]] = None


@dataclass
class TaskRequirement:
    """Task requirement information."""
    level: Optional[int] = None
    tasks: Optional[List['Task']] = None
    prerequisite_tasks: Optional[List[List['Task']]] = None


@dataclass
class Task:
    """Quest/task information."""
    id: str
    name: str
    trader: Optional[Trader] = None
    map: Optional['Map'] = None
    experience: Optional[int] = None
    wiki_link: Optional[str] = None
    min_player_level: Optional[int] = None
    objectives: Optional[List[TaskObjective]] = None
    start_rewards: Optional[TaskRewards] = None
    finish_rewards: Optional[TaskRewards] = None
    fail_conditions: Optional[List[Dict[str, Any]]] = None
    task_requirements: Optional[List[TaskRequirement]] = None
    # Additional fields
    normalized_name: Optional[str] = None
    fandom_link: Optional[str] = None
    task_image_link: Optional[str] = None
    kappaRequired: Optional[bool] = None
    lightkeeperRequired: Optional[bool] = None
    restartable: Optional[bool] = None
    descriptionMessageId: Optional[str] = None
    startMessageId: Optional[str] = None
    successMessageId: Optional[str] = None
    failMessageId: Optional[str] = None
    note: Optional[str] = None


@dataclass
class ContainedItem:
    """Item with quantity information."""
    item: Optional[Item]
    count: int
    quantity: Optional[int] = None
    attributes: Optional[List[dict]] = None


@dataclass
class PriceRequirement:
    """Deprecated - use level instead."""
    pass


@dataclass
class Craft:
    """Hideout crafting recipe."""
    id: str
    station: 'HideoutStation'
    level: int
    duration: int
    required_items: List[ContainedItem]
    reward_items: List[ContainedItem]
    source: str  # Deprecated
    requirements: Optional[List[Dict[str, Any]]] = None
    unlock_level: Optional[int] = None


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
    buy_limit: Optional[int] = None
    buy_limit_reset_time: Optional[int] = None


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
class LootContainer:
    """Loot container information."""
    id: str
    name: str
    normalized_name: Optional[str] = None


@dataclass
class MapExtract:
    """Map extraction point."""
    id: str
    name: str
    faction: Optional[str] = None
    switches: Optional[List[MapSwitch]] = None
    position: Optional[Dict[str, float]] = None
    outline: Optional[List[Dict[str, float]]] = None
    top: Optional[float] = None
    bottom: Optional[float] = None
    left: Optional[float] = None
    right: Optional[float] = None


@dataclass
class MapHazard:
    """Map hazard information."""
    name: str
    hazard_type: str
    position: Optional[Dict[str, float]] = None
    outline: Optional[List[Dict[str, float]]] = None
    top: Optional[float] = None
    bottom: Optional[float] = None
    left: Optional[float] = None
    right: Optional[float] = None


@dataclass
class MapLoot:
    """Map loot spawn information."""
    item: Item
    positions: Optional[List[Dict[str, float]]] = None


@dataclass
class MapSpawn:
    """Map spawn point."""
    position: Dict[str, float]
    sides: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    zoneName: Optional[str] = None


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
    # Additional comprehensive fields
    tarkov_data_id: Optional[str] = None
    access_keys: Optional[List[Item]] = None
    access_keys_min_player_level: Optional[int] = None
    extracts: Optional[List[MapExtract]] = None
    hazards: Optional[List[MapHazard]] = None
    locks: Optional[List[Dict[str, Any]]] = None
    loot_containers: Optional[List[LootContainer]] = None
    spawns: Optional[List[MapSpawn]] = None
    loot: Optional[List[MapLoot]] = None
    svg: Optional[str] = None


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
class HideoutStationLevel:
    """Hideout station level information."""
    level: int
    construction_time: Optional[int] = None
    description: Optional[str] = None
    item_requirements: Optional[List[ContainedItem]] = None
    station_level_requirements: Optional[List[Dict[str, Any]]] = None
    skill_requirements: Optional[List[Dict[str, Any]]] = None
    trader_requirements: Optional[List[Dict[str, Any]]] = None
    crafts: Optional[List[Craft]] = None
    bonuses: Optional[List[Dict[str, Any]]] = None


@dataclass
class HideoutStation:
    """Hideout station/module information."""
    id: str
    name: str
    normalized_name: Optional[str] = None
    image_link: Optional[str] = None
    levels: Optional[List[HideoutStationLevel]] = None
    tarkov_data_id: Optional[int] = None


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
    vendor: Optional[Trader]
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
    avg24h_price: Optional[int] = None
    avg7days_price: Optional[int] = None
    trader_name: Optional[str] = None
    trader_price: Optional[int] = None
    trader_price_rub: Optional[int] = None


@dataclass
class Status:
    """API status information."""
    name: str
    message: Optional[str] = None
    status: Optional[int] = None
    status_message: Optional[str] = None


@dataclass
class PlayerLevel:
    """Player level information."""
    level: int
    exp: int


@dataclass
class SkillLevel:
    """Skill level information."""
    name: str
    level: float


@dataclass
class HistoricalPricePoint:
    """Historical price data point."""
    price: Optional[int] = None
    price_min: Optional[int] = None
    timestamp: Optional[str] = None


@dataclass
class Lock:
    """Lock information."""
    id: str
    name: str
    normalized_name: Optional[str] = None
    needs_key: Optional[bool] = None
    key: Optional[Item] = None
    pick_strength: Optional[int] = None
    position: Optional[Dict[str, float]] = None
    outline: Optional[List[Dict[str, float]]] = None
    top: Optional[float] = None
    bottom: Optional[float] = None
    left: Optional[float] = None
    right: Optional[float] = None


@dataclass
class Mastering:
    """Weapon mastering information."""
    id: str
    weapons: Optional[List[Item]] = None
    level2: Optional[int] = None
    level3: Optional[int] = None


@dataclass
class QuestItem:
    """Quest-specific items with enhanced metadata."""
    id: str
    name: str
    short_name: Optional[str] = None
    description: Optional[str] = None
    base_price: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    icon_link: Optional[str] = None
    image_link: Optional[str] = None
    inspect_image_link: Optional[str] = None
    image_512px_link: Optional[str] = None
    image_8x_link: Optional[str] = None
    grid_image_link: Optional[str] = None
    wiki_link: Optional[str] = None
    used_in_tasks: Optional[List[Task]] = None
    received_from_tasks: Optional[List[Task]] = None


@dataclass
class GoonReport:
    """Community-driven goon squad sighting report."""
    id: str
    map: Optional['Map'] = None
    timestamp: Optional[str] = None
    location: Optional[str] = None
    spotted_by: Optional[str] = None
    verified: Optional[bool] = None


@dataclass
class HealthEffect:
    """Health effect information for medical items."""
    type: str
    value: Optional[float] = None
    duration: Optional[int] = None
    delay: Optional[int] = None


@dataclass
class HealthPart:
    """Body part health information."""
    body_parts: List[str]
    effects: List[HealthEffect]


@dataclass
class StimEffect:
    """Stimulant effect information."""
    type: str
    chance: Optional[float] = None
    delay: Optional[int] = None
    duration: Optional[int] = None
    value: Optional[float] = None
    percent: Optional[bool] = None
    skill_name: Optional[str] = None


@dataclass
class ItemCategory:
    """Enhanced item category with proper object structure."""
    id: str
    name: str
    normalized_name: Optional[str] = None
    parent: Optional['ItemCategory'] = None


@dataclass
class HandbookCategory:
    """In-game handbook category."""
    id: str
    name: str
    normalized_name: Optional[str] = None
    parent: Optional['HandbookCategory'] = None


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


def parse_task_objective_from_api(data: dict) -> TaskObjective:
    """Parse TaskObjective from API response data."""
    # Extract map names from map objects
    maps = []
    if data.get('maps'):
        for map_data in data.get('maps', []):
            if isinstance(map_data, dict):
                maps.append(map_data.get('name', 'Unknown'))
            else:
                maps.append(str(map_data))
    
    # Extract target names from target objects
    target = []
    if data.get('target'):
        for target_data in data.get('target', []):
            if isinstance(target_data, dict):
                target.append(target_data.get('name', 'Unknown'))
            else:
                target.append(str(target_data))
    
    return TaskObjective(
        id=data.get('id', ''),
        type_=data.get('type', ''),
        description=data.get('description', ''),
        maps=maps,
        optional=data.get('optional'),
        count=data.get('count'),
        found_in_raid=data.get('foundInRaid'),
        dog_tag_level=data.get('dogTagLevel'),
        player_level_min=data.get('playerLevelMin'),
        player_level_max=data.get('playerLevelMax'),
        target=target,
        target_item=parse_item_from_api(data.get('targetItem', {})) if data.get('targetItem') else None,
        zones=data.get('zones', [])
    )


def parse_task_requirement_from_api(data: dict) -> TaskRequirement:
    """Parse TaskRequirement from API response data."""
    # Note: To avoid circular dependencies, we'll store the raw task data
    # and parse it later if needed, or use task IDs instead of full objects
    return TaskRequirement(
        level=data.get('level'),
        tasks=None,  # Will be populated later to avoid circular dependencies
        prerequisite_tasks=None  # Will be populated later to avoid circular dependencies
    )


def parse_task_rewards_from_api(data: dict) -> TaskRewards:
    """Parse TaskRewards from API response data."""
    items = []
    if data.get('items'):
        items = [parse_contained_item_from_api(item_data) for item_data in data.get('items', [])]
    
    trader_unlock = []
    if data.get('traderUnlock'):
        trader_unlock = [parse_trader_from_api(trader_data) for trader_data in data.get('traderUnlock', [])]
    
    return TaskRewards(
        experience=data.get('experience'),
        reputation=data.get('reputation', []),
        items=items,
        offers=data.get('offers', []),
        skill_level_reward=data.get('skillLevelReward', []),
        trader_standing=data.get('traderStanding', []),
        trader_unlock=trader_unlock
    )


def parse_item_price_from_api(data: dict) -> ItemPrice:
    """Parse ItemPrice from API response data."""
    # Create a minimal vendor object to avoid circular dependencies
    vendor = None
    if data.get('vendor'):
        vendor_data = data.get('vendor', {})
        vendor = Trader(
            id=vendor_data.get('id', ''),
            name=vendor_data.get('name', ''),
            normalized_name=vendor_data.get('normalizedName'),
            description=vendor_data.get('description'),
            wiki_link=vendor_data.get('wikiLink'),
            image_link=vendor_data.get('imageLink'),
            levels=None,  # Don't parse levels to avoid circular dependencies
            currency=None,
            reset_time=vendor_data.get('resetTime'),
            discount=vendor_data.get('discount'),
            repair_currency=None
        )
    
    return ItemPrice(
        vendor=vendor,
        price=data.get('price', 0),
        currency=data.get('currency', 'RUB'),
        price_rub=data.get('priceRUB', data.get('price', 0)),
        updated=data.get('updated')
    )




def parse_trader_level_from_api(data: dict) -> TraderLevel:
    """Parse TraderLevel from API response data."""
    return TraderLevel(
        level=data.get('level', 1),
        required_player_level=data.get('requiredPlayerLevel', 1),
        required_reputation=data.get('requiredReputation', 0.0),
        required_commerce=data.get('requiredCommerce', 0),
        pay_rate=data.get('payRate', 1.0),
        insurance_rate=data.get('insuranceRate'),
        repair_rate=data.get('repairRate'),
        standing=data.get('standing')
    )


def parse_contained_item_from_api(data: dict) -> ContainedItem:
    """Parse ContainedItem from API response data."""
    item = None
    if data.get('item'):
        item = parse_item_from_api(data.get('item', {}))
    
    return ContainedItem(
        item=item,
        count=data.get('count', 1),
        quantity=data.get('quantity', 1),
        attributes=data.get('attributes', [])
    )


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
        category=data.get('category'),
        # Additional comprehensive fields
        normalized_name=data.get('normalizedName'),
        background_color=data.get('backgroundColor'),
        width=data.get('width'),
        height=data.get('height'),
        grid_width=data.get('gridWidth'),
        grid_height=data.get('gridHeight'),
        fleamarket_fee=data.get('fleaMarketFee'),
        accuracy_modifier=data.get('accuracyModifier'),
        recoil_modifier=data.get('recoilModifier'),
        ergonomics_modifier=data.get('ergonomicsModifier'),
        has_grid=data.get('hasGrid'),
        blocks_headphones=data.get('blocksHeadphones'),
        link=data.get('link'),
        sell_for=[parse_item_price_from_api(price) for price in data.get('sellFor', [])],
        buy_for=[parse_item_price_from_api(price) for price in data.get('buyFor', [])],
        used_in_tasks=data.get('usedInTasks', []),  # Keep as raw data to avoid circular deps
        received_from_tasks=data.get('receivedFromTasks', []),  # Keep as raw data to avoid circular deps
        barters_for=data.get('bartersFor', []),  # Keep as raw data to avoid circular deps
        barters_using=data.get('bartersUsing', []),  # Keep as raw data to avoid circular deps
        crafts_for=data.get('craftsFor', []),  # Keep as raw data to avoid circular deps
        crafts_using=data.get('craftsUsing', []),  # Keep as raw data to avoid circular deps
        properties=data.get('properties')
    )


def parse_trader_from_api(data: dict) -> Trader:
    """Parse Trader from API response data."""
    currency_data = data.get('currency', {})
    currency = parse_item_from_api(currency_data) if currency_data else None
    
    repair_currency_data = data.get('repairCurrency', {})
    repair_currency = parse_item_from_api(repair_currency_data) if repair_currency_data else None
    
    return Trader(
        id=data.get('id', ''),
        name=data.get('name', ''),
        normalized_name=data.get('normalizedName'),
        description=data.get('description'),
        wiki_link=data.get('wikiLink'),
        image_link=data.get('imageLink'),
        levels=[parse_trader_level_from_api(level) for level in data.get('levels', [])],
        currency=currency,
        reset_time=data.get('resetTime'),
        discount=data.get('discount'),
        repair_currency=repair_currency,
        cash_offers=data.get('cashOffers', [])
    )


def parse_task_from_api(data: dict) -> Task:
    """Parse Task from API response data."""
    trader_data = data.get('trader', {})
    trader = parse_trader_from_api(trader_data) if trader_data else None
    
    map_data = data.get('map', {})
    map_obj = parse_map_from_api(map_data) if map_data else None
    
    return Task(
        id=data.get('id', ''),
        name=data.get('name', ''),
        trader=trader,
        map=map_obj,
        experience=data.get('experience'),
        wiki_link=data.get('wikiLink'),
        min_player_level=data.get('minPlayerLevel'),
        objectives=[parse_task_objective_from_api(obj) for obj in data.get('objectives', [])],
        start_rewards=parse_task_rewards_from_api(data.get('startRewards', {})) if data.get('startRewards') else None,
        finish_rewards=parse_task_rewards_from_api(data.get('finishRewards', {})) if data.get('finishRewards') else None,
        fail_conditions=data.get('failConditions', []),
        task_requirements=[parse_task_requirement_from_api(req) for req in data.get('taskRequirements', [])],
        normalized_name=data.get('normalizedName'),
        fandom_link=data.get('fandomLink'),
        task_image_link=data.get('taskImageLink'),
        kappaRequired=data.get('kappaRequired'),
        lightkeeperRequired=data.get('lightkeeperRequired'),
        restartable=data.get('restartable'),
        descriptionMessageId=data.get('descriptionMessageId'),
        startMessageId=data.get('startMessageId'),
        successMessageId=data.get('successMessageId'),
        failMessageId=data.get('failMessageId'),
        note=data.get('note')
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
        nameId=data.get('nameId'),
        tarkov_data_id=data.get('tarkovDataId'),
        access_keys=data.get('accessKeys', []),
        access_keys_min_player_level=data.get('accessKeysMinPlayerLevel'),
        extracts=data.get('extracts', []),
        hazards=data.get('hazards', []),
        locks=data.get('locks', []),
        loot_containers=data.get('lootContainers', []),
        spawns=data.get('spawns', []),
        loot=data.get('loot', []),
        svg=data.get('svg')
    )


def parse_barter_from_api(data: dict) -> Barter:
    """Parse Barter from API response data."""
    trader_data = data.get('trader', {})
    trader = parse_trader_from_api(trader_data) if trader_data else None
    
    task_data = data.get('taskUnlock', {})
    task = parse_task_from_api(task_data) if task_data else None
    
    return Barter(
        id=data.get('id', ''),
        trader=trader,
        level=data.get('level', 0),
        task_unlock=task,
        required_items=data.get('requiredItems', []),
        reward_items=data.get('rewardItems', []),
        source=data.get('source', ''),
        source_name=data.get('sourceName'),
        requirements=data.get('requirements', []),
        buy_limit=data.get('buyLimit'),
        buy_limit_reset_time=data.get('buyLimitResetTime')
    )


def parse_craft_from_api(data: dict) -> Craft:
    """Parse Craft from API response data."""
    station_data = data.get('station', {})
    station = HideoutStation(
        id=station_data.get('id', ''),
        name=station_data.get('name', ''),
        normalized_name=station_data.get('normalizedName')
    ) if station_data else None
    
    return Craft(
        id=data.get('id', ''),
        station=station,
        level=data.get('level', 0),
        duration=data.get('duration', 0),
        required_items=data.get('requiredItems', []),
        reward_items=data.get('rewardItems', []),
        source=data.get('source', ''),
        requirements=data.get('requirements', []),
        unlock_level=data.get('unlockLevel')
    )


def parse_ammo_from_api(data: dict) -> Ammo:
    """Parse Ammo from API response data."""
    item_data = data.get('item', {})
    item = parse_item_from_api(item_data) if item_data else Item(id='', name='')
    
    return Ammo(
        item=item,
        weight=data.get('weight', 0.0),
        caliber=data.get('caliber'),
        stack_max_size=data.get('stackMaxSize', 1),
        tracer=data.get('tracer', False),
        tracer_color=data.get('tracerColor'),
        ammo_type=data.get('ammoType', ''),
        projectile_count=data.get('projectileCount'),
        damage=data.get('damage', 0),
        armor_damage=data.get('armorDamage', 0),
        fragmentation_chance=data.get('fragmentationChance', 0.0),
        ricochet_chance=data.get('ricochetChance', 0.0),
        penetration_chance=data.get('penetrationChance', 0.0),
        penetration_power=data.get('penetrationPower', 0),
        penetration_power_deviation=data.get('penetrationPowerDeviation'),
        accuracy_modifier=data.get('accuracyModifier'),
        recoil_modifier=data.get('recoilModifier'),
        initial_speed=data.get('initialSpeed'),
        light_bleed_modifier=data.get('lightBleedModifier', 0.0),
        heavy_bleed_modifier=data.get('heavyBleedModifier', 0.0),
        stamina_burn_per_damage=data.get('staminaBurnPerDamage')
    )


def parse_hideout_station_from_api(data: dict) -> HideoutStation:
    """Parse HideoutStation from API response data."""
    return HideoutStation(
        id=data.get('id', ''),
        name=data.get('name', ''),
        normalized_name=data.get('normalizedName'),
        image_link=data.get('imageLink'),
        levels=data.get('levels', []),
        tarkov_data_id=data.get('tarkovDataId')
    )
