"""GraphQL client for Tarkov API."""

import asyncio
import time
from typing import Dict, Any, Optional, List
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import aiohttp
import logging

from config import config

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
            return result
        except Exception as e:
            logger.error(f"GraphQL query failed: {e}")
            raise
    
    async def search_items(self, name: Optional[str] = None, item_type: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Search for items by name or type."""
        query = """
        query SearchItems($name: String, $type: String, $limit: Int) {
            items(name: $name, type: $type, limit: $limit) {
                id
                name
                shortName
                description
                basePrice
                weight
                width
                height
                iconLink
                wikiLink
                types
                updated
                avg24hPrice
                sellFor {
                    source
                    price
                    currency
                    priceRUB
                }
                buyFor {
                    source
                    price
                    currency
                    priceRUB
                }
            }
        }
        """
        
        variables = {"limit": limit}
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
                description
                basePrice
                weight
                width
                height
                iconLink
                wikiLink
                types
                updated
                avg24hPrice
                low24hPrice
                high24hPrice
                lastLowPrice
                changeLast48h
                changeLast48hPercent
                sellFor {
                    source
                    price
                    currency
                    priceRUB
                    requirements {
                        type
                        value
                    }
                }
                buyFor {
                    source
                    price
                    currency
                    priceRUB
                    requirements {
                        type
                        value
                    }
                }
                containsItems {
                    item {
                        id
                        name
                    }
                    count
                }
                usedInTasks {
                    id
                    name
                    trader {
                        name
                    }
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
                    name
                    resetTime
                }
                level
                buyLimit
                requiredItems {
                    item {
                        id
                        name
                        avg24hPrice
                    }
                    count
                }
                rewardItems {
                    item {
                        id
                        name
                        avg24hPrice
                    }
                    count
                }
                taskUnlock {
                    id
                    name
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
        """Get hideout modules and their requirements."""
        query = """
        query GetHideoutModules {
            hideoutModules {
                id
                name
                level
                require {
                    item {
                        id
                        name
                    }
                    count
                    module {
                        name
                    }
                    level
                    skill {
                        name
                    }
                    trader {
                        name
                    }
                }
                bonuses {
                    type
                    value
                }
                crafts {
                    duration
                    requiredItems {
                        item {
                            id
                            name
                        }
                        count
                    }
                    rewardItems {
                        item {
                            id
                            name
                        }
                        count
                    }
                }
            }
        }
        """
        
        result = await self.execute_query(query)
        return result.get("hideoutModules", [])
