"""Tests for GraphQL client."""

import pytest                                                                                                                                                 
import asyncio                                                                                                                                                
from unittest.mock import AsyncMock, patch, MagicMock                                                                                                         
from src.graphql_client import TarkovGraphQLClient, RateLimiter                                                                                               
                                                                                                                                                              
# Set timeout for all async tests to prevent hanging                                                                                                          
pytestmark = pytest.mark.timeout(30) 

class TestRateLimiter:
    """Test rate limiter functionality."""
    
    @pytest.mark.asyncio
    async def test_rate_limiter_allows_requests_under_limit(self):
        """Test that rate limiter allows requests under the limit."""
        limiter = RateLimiter(max_requests=5, time_window=60)
        
        # Should allow 5 requests without delay
        for _ in range(5):
            await limiter.acquire()
        
        # Check that we have 5 requests recorded
        assert len(limiter.requests) == 5
    
    @pytest.mark.asyncio                                                                                                                                      
    async def test_rate_limiter_blocks_excess_requests(self):                                                                                                 
        """Test that rate limiter blocks requests over the limit."""                                                                                          
        limiter = RateLimiter(max_requests=2, time_window=0.1)  # Use shorter time window                                                                     
                                                                                                                                                              
        # Allow 2 requests                                                                                                                                    
        await limiter.acquire()                                                                                                                               
        await limiter.acquire()                                                                                                                               
                                                                                                                                                              
        # Third request should be delayed                                                                                                                     
        start_time = asyncio.get_event_loop().time()                                                                                                          
        await limiter.acquire()                                                                                                                               
        end_time = asyncio.get_event_loop().time()                                                                                                            
                                                                                                                                                              
        # Should have been delayed by approximately 0.1 seconds                                                                                               
        assert end_time - start_time >= 0.05  # Allow some tolerance  

class TestTarkovGraphQLClient:
    """Test GraphQL client functionality."""
    
    @pytest.fixture
    def mock_client_response(self):
        """Mock GraphQL client response."""
        return {
            "items": [
                {
                    "id": "test-id-1",
                    "name": "Test Item",
                    "shortName": "TI",
                    "avg24hPrice": 10000,
                    "types": ["weapon"]
                }
            ]
        }
    
    @pytest.mark.asyncio
    async def test_search_items_success(self, mock_client_response):
        """Test successful item search."""
        with patch('src.graphql_client.Client') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.execute_async.return_value = mock_client_response
            mock_client_class.return_value = mock_client
            
            with patch('src.graphql_client.aiohttp.ClientSession'):
                async with TarkovGraphQLClient() as client:
                    result = await client.search_items(name="Test")
                
                assert len(result) == 1
                assert result[0]["name"] == "Test Item"
                assert result[0]["id"] == "test-id-1"
    
    @pytest.mark.asyncio
    async def test_get_item_by_id_success(self):
        """Test successful item retrieval by ID."""
        mock_response = {
            "item": {
                "id": "test-id",
                "name": "Test Item",
                "shortName": "TI",
                "description": "A test item",
                "avg24hPrice": 15000
            }
        }
        
        with patch('src.graphql_client.Client') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.execute_async.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            with patch('src.graphql_client.aiohttp.ClientSession'):
                async with TarkovGraphQLClient() as client:
                    result = await client.get_item_by_id("test-id")

                assert result
                assert result["name"] == "Test Item"
                assert result["id"] == "test-id"
    
    @pytest.mark.asyncio
    async def test_get_item_by_id_not_found(self):
        """Test item not found scenario."""
        mock_response = {"item": None}
        
        with patch('src.graphql_client.Client') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.execute_async.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            with patch('src.graphql_client.aiohttp.ClientSession'):
                async with TarkovGraphQLClient() as client:
                    result = await client.get_item_by_id("nonexistent")
                
                assert result is None
    
    @pytest.mark.asyncio
    async def test_get_barters_success(self):
        """Test successful barter retrieval."""
        mock_response = {
            "barters": [
                {
                    "id": "barter-1",
                    "trader": {"name": "Prapor"},
                    "level": 1,
                    "requiredItems": [
                        {
                            "item": {"id": "item-1", "name": "Item 1", "avg24hPrice": 5000},
                            "count": 2
                        }
                    ],
                    "rewardItems": [
                        {
                            "item": {"id": "item-2", "name": "Item 2", "avg24hPrice": 12000},
                            "count": 1
                        }
                    ]
                }
            ]
        }
        
        with patch('src.graphql_client.Client') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.execute_async.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            with patch('src.graphql_client.aiohttp.ClientSession'):
                async with TarkovGraphQLClient() as client:
                    result = await client.get_barters(limit=10)
                
                assert len(result) == 1
                assert result[0]["id"] == "barter-1"
                assert result[0]["trader"]["name"] == "Prapor"
    
    @pytest.mark.asyncio
    async def test_client_error_handling(self):
        """Test client error handling."""
        with patch('src.graphql_client.Client') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.execute_async.side_effect = Exception("Network error")
            mock_client_class.return_value = mock_client
            
            with patch('src.graphql_client.aiohttp.ClientSession'):
                async with TarkovGraphQLClient() as client:
                    with pytest.raises(Exception, match="Network error"):
                        await client.search_items(name="Test")