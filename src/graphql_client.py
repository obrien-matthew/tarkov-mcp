"""GraphQL client for Tarkov API."""

import asyncio
import time
from typing import Dict, Any, Optional, List
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import aiohttp
import logging

from .config import config

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple rate limiter for API requests."""
    
    def __init__(self, max_requests: int, time_window: int = 60):
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
        
        timeout = aiohttp.ClientTimeout(total=config.REQUEST_TIMEOUT)
        self._session = aiohttp.ClientSession(
            headers=headers,
            timeout=timeout
        )
        
        transport = AIOHTTPTransport(
            url=config.TARKOV_API_URL,
            session=self._session
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