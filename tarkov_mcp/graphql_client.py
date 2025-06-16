"""GraphQL client for Tarkov API."""

import asyncio
import time
from typing import Dict, Any, Optional, List
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import aiohttp
import logging

from tarkov_mcp.config import config

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple rate limiter for API requests."""
    
    def __init__(self, max_requests: int, time_window: float = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to make a request."""
        async with self._lock:
            now = time.time()
            # Remove old requests outside the time window
            self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
            
            if len(self.requests) >= self.max_requests:
                # Calculate how long to wait
                oldest_request = min(self.requests)
                wait_time = self.time_window - (now - oldest_request)
                if wait_time > 0:
                    logger.info(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                    await asyncio.sleep(wait_time)
                    return await self.acquire()
            
            self.requests.append(now)

class TarkovGraphQLClient:
    """GraphQL client for Tarkov API with rate limiting and error handling."""
    
    def __init__(self):
        self.rate_limiter = RateLimiter(config.MAX_REQUESTS_PER_MINUTE)
        self._client: Optional[Client] = None
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._cleanup()
    
    async def _initialize(self):
        """Initialize the GraphQL client."""
        headers = {
            "User-Agent": config.USER_AGENT,
            "Content-Type": "application/json"
        }
        
        transport = AIOHTTPTransport(
            url=config.TARKOV_API_URL,
            headers=headers,
            timeout=config.REQUEST_TIMEOUT
        )
        
        self._client = Client(transport=transport, fetch_schema_from_transport=False)
    
    async def _cleanup(self):
        """Clean up resources."""
        if self._session:
            await self._session.close()
    
    async def execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a GraphQL query with rate limiting."""
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        await self.rate_limiter.acquire()
        
        try:
            gql_query = gql(query)
            result = await self._client.execute_async(gql_query, variable_values=variables)
            logger.debug(f"GraphQL query executed successfully. Variables: {variables}")
            return result
        except Exception as e:
            logger.error(f"GraphQL query failed: {e}. Query variables: {variables}")
            raise
    
    async def search_items(self, name: Optional[str] = None, item_type: Optional[str] = None, limit: int = 50, lang: str = "en") -> List[Dict[str, Any]]:
        """Search for items by name or type."""
        query = """
        query SearchItems($name: String, $type: String, $limit: Int, $lang: LanguageCode) {
            items(name: $name, type: $type, limit: $limit, lang: $lang) {
                id
                name
                shortName
                normalizedName
                description
                basePrice
                weight
                width
                height
                gridWidth
                gridHeight
                iconLink
                wikiLink
                imageLink
                gridImageLink
                baseImageLink
                inspectImageLink
                image512pxLink
                image8xLink
                backgroundColor
                types
                category {
                    id
                    name
                    normalizedName
                }
                categories {
                    id
                    name
                    normalizedName
                }
                bsgCategoryId
                handbookCategories {
                    id
                    name
                    normalizedName
                }
                updated
                avg24hPrice
                low24hPrice
                high24hPrice
                lastLowPrice
                lastOfferCount
                changeLast48h
                changeLast48hPercent
                fleaMarketFee
                accuracyModifier
                recoilModifier
                ergonomicsModifier
                hasGrid
                blocksHeadphones
                link
                velocity
                loudness
                properties {
                    ... on ItemPropertiesWeapon {
                        caliber
                        effectiveDistance
                        ergonomics
                        fireModes
                        fireRate
                        maxDurability
                        recoilVertical
                        recoilHorizontal
                        centerOfImpact
                        deviationCurve
                        deviationMax
                        recoilDispersion
                        recoilAngle
                        cameraRecoil
                        cameraSnap
                        convergence
                        defaultWidth
                        defaultHeight
                        defaultErgonomics
                        defaultWeight
                        defaultRecoilVertical
                        defaultRecoilHorizontal
                        allowedAmmo {
                            item {
                                id
                                name
                                shortName
                            }
                        }
                    }
                    ... on ItemPropertiesArmor {
                        class
                        durability
                        material {
                            id
                            name
                            destructibility
                            minRepairDegradation
                            maxRepairDegradation
                            explosionDestructibility
                            minRepairKitDegradation
                            maxRepairKitDegradation
                        }
                        bluntThroughput
                        zones
                        armorType
                        ergonomicsPenalty
                        speedPenalty
                        turnPenalty
                    }
                    ... on ItemPropertiesHelmet {
                        class
                        durability
                        material {
                            id
                            name
                            destructibility
                        }
                        bluntThroughput
                        zones
                        ergonomicsPenalty
                        speedPenalty
                        turnPenalty
                        deafening
                        blocksHeadset
                    }
                    ... on ItemPropertiesContainer {
                        capacity
                        grids {
                            width
                            height
                        }
                    }
                    ... on ItemPropertiesFoodDrink {
                        energy
                        hydration
                        stimEffects {
                            type
                            chance
                            delay
                            duration
                            value
                            percent
                            skillName
                        }
                    }
                    ... on ItemPropertiesGrenade {
                        type
                        fuse
                        minExplosionDistance
                        maxExplosionDistance
                        fragments
                        contusionRadius
                    }
                    ... on ItemPropertiesKey {
                        uses
                    }
                    ... on ItemPropertiesMedicalItem {
                        uses
                        useTime
                        cures
                        healthEffects {
                            bodyParts
                            effects {
                                type
                                value
                                duration
                                delay
                            }
                        }
                    }
                    ... on ItemPropertiesStim {
                        uses
                        useTime
                        cures
                        stimEffects {
                            type
                            chance
                            delay
                            duration
                            value
                            percent
                            skillName
                        }
                    }
                    ... on ItemPropertiesAmmo {
                        caliber
                        stackMaxSize
                        tracer
                        tracerColor
                        ammoType
                        projectileCount
                        damage
                        armorDamage
                        fragmentationChance
                        ricochetChance
                        penetrationChance
                        penetrationPower
                        penetrationPowerDeviation
                        accuracyModifier
                        recoilModifier
                        initialSpeed
                        lightBleedModifier
                        heavyBleedModifier
                        staminaBurnPerDamage
                    }
                    ... on ItemPropertiesBackpack {
                        capacity
                        grids {
                            width
                            height
                        }
                        penalties {
                            speed
                            mouse
                            deafness
                        }
                    }
                    ... on ItemPropertiesChestRig {
                        class
                        durability
                        capacity
                        grids {
                            width
                            height
                        }
                        material {
                            id
                            name
                        }
                        zones
                        armorType
                        ergonomicsPenalty
                        speedPenalty
                        turnPenalty
                    }
                }
                sellFor {
                    vendor {
                        name
                        normalizedName
                    }
                    price
                    currency
                    priceRUB
                    updated
                }
                buyFor {
                    vendor {
                        name
                        normalizedName
                    }
                    price
                    currency
                    priceRUB
                    updated
                }
            }
        }
        """
        
        variables = {"limit": limit, "lang": lang}
        if name:
            variables["name"] = name
        if item_type:
            variables["type"] = item_type
        
        result = await self.execute_query(query, variables)
        return result.get("items", [])
    
    async def get_item_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed item information by ID."""
        query = """
        query GetItem($id: ID!) {
            item(id: $id) {
                id
                name
                shortName
                normalizedName
                description
                basePrice
                weight
                width
                height
                gridWidth
                gridHeight
                iconLink
                wikiLink
                imageLink
                gridImageLink
                baseImageLink
                backgroundColor
                types
                category
                updated
                avg24hPrice
                low24hPrice
                high24hPrice
                lastLowPrice
                changeLast48h
                changeLast48hPercent
                fleaMarketFee
                accuracyModifier
                recoilModifier
                ergonomicsModifier
                hasGrid
                blocksHeadphones
                link
                properties {
                    ... on WeaponProperties {
                        caliber
                        effectiveDistance
                        ergonomics
                        fireModes
                        fireRate
                        maxDurability
                        recoilVertical
                        recoilHorizontal
                        centerOfImpact
                        cameraRecoil
                        cameraSnap
                        convergence
                        slots {
                            id
                            name
                            nameId
                            required
                        }
                    }
                    ... on ArmorProperties {
                        class
                        durability
                        material {
                            id
                            name
                            destructibility
                            minRepairDegradation
                            maxRepairDegradation
                            explosionDestructibility
                            minRepairKitDegradation
                            maxRepairKitDegradation
                        }
                        bluntThroughput
                        zones
                        armorType
                        ergonomicsPenalty
                        speedPenalty
                        turnPenalty
                    }
                    ... on HelmetProperties {
                        class
                        durability
                        material {
                            id
                            name
                            destructibility
                        }
                        bluntThroughput
                        zones
                        ergonomicsPenalty
                        speedPenalty
                        turnPenalty
                        deafening
                        blocksHeadset
                        slots {
                            id
                            name
                            nameId
                            required
                        }
                    }
                    ... on ContainerProperties {
                        capacity
                        grids {
                            width
                            height
                        }
                    }
                    ... on FoodDrinkProperties {
                        energy
                        hydration
                    }
                    ... on GrenadeProperties {
                        type
                        fuse
                        minExplosionDistance
                        maxExplosionDistance
                        fragments
                        contusionRadius
                    }
                    ... on KeyProperties {
                        uses
                    }
                    ... on MedicalProperties {
                        uses
                        useTime
                        cures
                    }
                    ... on StimulantsProperties {
                        uses
                        useTime
                        cures
                    }
                }
                sellFor {
                    vendor {
                        name
                        normalizedName
                    }
                    price
                    currency
                    priceRUB
                    updated
                }
                buyFor {
                    vendor {
                        name
                        normalizedName
                    }
                    price
                    currency
                    priceRUB
                    updated
                }
                usedInTasks {
                    id
                    name
                    trader {
                        name
                    }
                }
                receivedFromTasks {
                    id
                    name
                    trader {
                        name
                    }
                }
                bartersFor {
                    id
                    trader {
                        name
                    }
                    level
                }
                bartersUsing {
                    id
                    trader {
                        name
                    }
                    level
                }
                craftsFor {
                    id
                    station {
                        name
                    }
                    level
                }
                craftsUsing {
                    id
                    station {
                        name
                    }
                    level
                }
            }
        }
        """
        
        result = await self.execute_query(query, {"id": item_id})
        return result.get("item")
    
    async def get_flea_market_data(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get current flea market data."""
        query = """
        query GetFleaMarket($limit: Int) {
            items(limit: $limit) {
                id
                name
                shortName
                avg24hPrice
                low24hPrice
                high24hPrice
                lastLowPrice
                changeLast48h
                changeLast48hPercent
                updated
                sellFor {
                    source
                    price
                    currency
                    priceRUB
                }
            }
        }
        """
        
        result = await self.execute_query(query, {"limit": limit})
        return result.get("items", [])
    
    async def get_barters(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get available barter trades."""
        query = """
        query GetBarters($limit: Int) {
            barters(limit: $limit) {
                id
                trader {
                    id
                    name
                    normalizedName
                    resetTime
                }
                level
                buyLimit
                buyLimitResetTime
                requiredItems {
                    item {
                        id
                        name
                        shortName
                        iconLink
                        basePrice
                        avg24hPrice
                    }
                    count
                    quantity
                    attributes {
                        name
                        value
                    }
                }
                rewardItems {
                    item {
                        id
                        name
                        shortName
                        iconLink
                        basePrice
                        avg24hPrice
                    }
                    count
                    quantity
                    attributes {
                        name
                        value
                    }
                }
                taskUnlock {
                    id
                    name
                    trader {
                        name
                    }
                }
            }
        }
        """
        
        result = await self.execute_query(query, {"limit": limit})
        return result.get("barters", [])
    
    async def get_maps(self) -> List[Dict[str, Any]]:
        """Get all available maps."""
        query = """
        query GetMaps {
            maps {
                id
                name
                description
                wiki
                raidDuration
                players
                enemies
                bosses {
                    name
                    spawnChance
                    spawnLocations {
                        name
                        chance
                    }
                    escorts {
                        name
                        amount {
                            min
                            max
                        }
                    }
                }
                extracts {
                    name
                    faction
                    switches {
                        name
                    }
                }
                loot {
                    item {
                        id
                        name
                        avg24hPrice
                    }
                    spawnChance
                }
            }
        }
        """
        
        result = await self.execute_query(query)
        return result.get("maps", [])
    
    async def get_map_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get detailed map information by name."""
        query = """
        query GetMap($name: String!) {
            maps(name: $name) {
                id
                name
                description
                wiki
                raidDuration
                players
                enemies
                bosses {
                    name
                    spawnChance
                    spawnLocations {
                        name
                        chance
                    }
                    escorts {
                        name
                        amount {
                            min
                            max
                        }
                    }
                }
                extracts {
                    name
                    faction
                    switches {
                        name
                    }
                }
                loot {
                    item {
                        id
                        name
                        avg24hPrice
                    }
                    spawnChance
                }
            }
        }
        """
        
        result = await self.execute_query(query, {"name": name})
        maps = result.get("maps", [])
        return maps[0] if maps else None
    
    async def get_traders(self) -> List[Dict[str, Any]]:
        """Get all traders."""
        query = """
        query GetTraders {
            traders {
                id
                name
                description
                location
                resetTime
                currency {
                    name
                }
                levels {
                    level
                    requiredPlayerLevel
                    requiredReputation
                    requiredCommerce
                    paywall {
                        level
                    }
                }
                insurance {
                    availableOnMap
                    minReturnHour
                    maxReturnHour
                    maxStorageTime
                }
                repair {
                    availability
                    priceModifier
                    qualityModifier
                }
            }
        }
        """
        
        result = await self.execute_query(query)
        return result.get("traders", [])
    
    async def get_trader_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get detailed trader information by name."""
        query = """
        query GetTrader($name: String!) {
            traders(name: $name) {
                id
                name
                description
                location
                resetTime
                currency {
                    name
                }
                levels {
                    level
                    requiredPlayerLevel
                    requiredReputation
                    requiredCommerce
                    paywall {
                        level
                    }
                }
                insurance {
                    availableOnMap
                    minReturnHour
                    maxReturnHour
                    maxStorageTime
                }
                repair {
                    availability
                    priceModifier
                    qualityModifier
                }
            }
        }
        """
        
        result = await self.execute_query(query, {"name": name})
        traders = result.get("traders", [])
        return traders[0] if traders else None
    
    async def get_trader_items(self, trader_name: str, level: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get items sold by a trader."""
        query = """
        query GetTraderItems($trader: String!, $level: Int) {
            traders(name: $trader) {
                cashOffers(level: $level) {
                    item {
                        id
                        name
                        shortName
                        types
                        avg24hPrice
                    }
                    priceRUB
                    currency
                    minTraderLevel
                    buyLimit
                    restockAmount
                    requirements {
                        type
                        value
                        stringValue
                    }
                }
            }
        }
        """
        
        variables = {"trader": trader_name}
        if level:
            variables["level"] = level
        
        result = await self.execute_query(query, variables)
        traders = result.get("traders", [])
        if traders:
            return traders[0].get("cashOffers", [])
        return []
    
    async def get_quests(self, trader: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all quests, optionally filtered by trader."""
        query = """
        query GetQuests($trader: String) {
            tasks(trader: $trader) {
                id
                name
                trader {
                    name
                }
                minPlayerLevel
                experience
                taskRequirements {
                    task {
                        id
                        name
                    }
                }
            }
        }
        """
        
        variables = {}
        if trader:
            variables["trader"] = trader
        
        result = await self.execute_query(query, variables)
        return result.get("tasks", [])
    
    async def get_quest_by_id(self, quest_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed quest information by ID."""
        query = """
        query GetQuest($id: ID!) {
            task(id: $id) {
                id
                name
                description
                wikiLink
                trader {
                    name
                }
                minPlayerLevel
                experience
                taskRequirements {
                    task {
                        id
                        name
                    }
                }
                objectives {
                    id
                    description
                    optional
                    target {
                        name
                    }
                    maps {
                        name
                    }
                }
                finishRewards {
                    items {
                        item {
                            id
                            name
                        }
                        count
                    }
                    traderStanding {
                        trader {
                            name
                        }
                        standing
                    }
                    traderUnlock {
                        name
                    }
                    skillLevelReward {
                        name
                        level
                    }
                }
            }
        }
        """
        
        result = await self.execute_query(query, {"id": quest_id})
        return result.get("task")
    
    async def search_quests(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search for quests by name or description."""
        gql_query = """
        query SearchQuests($name: String, $limit: Int) {
            tasks(name: $name, limit: $limit) {
                id
                name
                description
                trader {
                    name
                }
                minPlayerLevel
                experience
            }
        }
        """
        
        result = await self.execute_query(gql_query, {"name": query, "limit": limit})
        return result.get("tasks", [])
    
    async def get_ammo_data(self, caliber: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get ammunition data."""
        query = """
        query GetAmmo($caliber: String, $limit: Int) {
            ammo(caliber: $caliber, limit: $limit) {
                item {
                    id
                    name
                    shortName
                    avg24hPrice
                }
                caliber
                damage
                penetrationPower
                armorDamage
                fragmentationChance
                ricochetChance
                lightBleedModifier
                heavyBleedModifier
            }
        }
        """
        
        variables = {"limit": limit}
        if caliber:
            variables["caliber"] = caliber
        
        result = await self.execute_query(query, variables)
        return result.get("ammo", [])
    
    async def get_hideout_modules(self) -> List[Dict[str, Any]]:
        """Get hideout modules/stations."""
        query = """
        query GetHideoutStations {
            hideoutStations {
                id
                name
                normalizedName
                imageLink
                tarkovDataId
                levels {
                    level
                    constructionTime
                    description
                    itemRequirements {
                        item {
                            id
                            name
                            shortName
                            iconLink
                        }
                        count
                        quantity
                        attributes {
                            name
                            value
                        }
                    }
                    stationLevelRequirements {
                        station {
                            id
                            name
                            normalizedName
                        }
                        level
                    }
                    skillRequirements {
                        name
                        level
                    }
                    traderRequirements {
                        trader {
                            id
                            name
                            normalizedName
                        }
                        level
                    }
                    crafts {
                        id
                        duration
                        requiredItems {
                            item {
                                id
                                name
                                shortName
                            }
                            count
                        }
                        rewardItems {
                            item {
                                id
                                name
                                shortName
                            }
                            count
                        }
                    }
                    bonuses {
                        name
                        value
                        type
                        passive
                        production
                        visible
                    }
                }
            }
        }
        """
        
        result = await self.execute_query(query)
        return result.get("hideoutStations", [])

    async def get_crafts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all crafting recipes."""
        query = """
        query GetCrafts($limit: Int) {
            crafts(limit: $limit) {
                id
                station {
                    id
                    name
                    normalizedName
                }
                level
                duration
                unlockLevel
                requiredItems {
                    item {
                        id
                        name
                        shortName
                        iconLink
                        basePrice
                        avg24hPrice
                    }
                    count
                    quantity
                    attributes {
                        name
                        value
                    }
                }
                rewardItems {
                    item {
                        id
                        name
                        shortName
                        iconLink
                        basePrice
                        avg24hPrice
                    }
                    count
                    quantity
                    attributes {
                        name
                        value
                    }
                }
            }
        }
        """
        
        variables = {"limit": limit}
        result = await self.execute_query(query, variables)
        return result.get("crafts", [])

    async def get_quest_items(self, limit: int = 50, lang: str = "en") -> List[Dict[str, Any]]:
        """Get quest-specific items."""
        query = """
        query GetQuestItems($limit: Int, $lang: LanguageCode) {
            questItems(limit: $limit, lang: $lang) {
                id
                name
                shortName
                description
                basePrice
                width
                height
                iconLink
                imageLink
                inspectImageLink
                image512pxLink
                image8xLink
                gridImageLink
                wikiLink
                usedInTasks {
                    id
                    name
                    trader {
                        name
                    }
                    minPlayerLevel
                    experience
                }
                receivedFromTasks {
                    id
                    name
                    trader {
                        name
                    }
                    minPlayerLevel
                    experience
                }
            }
        }
        """
        
        variables = {"limit": limit, "lang": lang}
        result = await self.execute_query(query, variables)
        return result.get("questItems", [])

    async def get_goon_reports(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent goon squad sighting reports."""
        query = """
        query GetGoonReports($limit: Int) {
            goonReports(limit: $limit) {
                id
                map {
                    id
                    name
                }
                timestamp
                location
                spottedBy
                verified
            }
        }
        """
        
        variables = {"limit": limit}
        result = await self.execute_query(query, variables)
        return result.get("goonReports", [])
