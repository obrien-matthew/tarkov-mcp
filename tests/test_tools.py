"""Tests for MCP tools."""
                                                                                                                                                              
import pytest                                                                                                                                                 
from unittest.mock import AsyncMock, patch                                                                                                                    
from mcp.types import TextContent                                                                                                                             
                                                                                                                                                              
from src.tools.items import ItemTools                                                                                                                         
from src.tools.market import MarketTools                                                                                                                      
                                                                                                                                                              
# Set timeout for all async tests to prevent hanging                                                                                                          
pytestmark = pytest.mark.timeout(30)     
class TestItemTools:
    """Test item tools functionality."""
    
    @pytest.fixture
    def item_tools(self):
        """Create ItemTools instance."""
        return ItemTools()
    
    @pytest.fixture
    def mock_search_response(self):
        """Mock search response."""
        return [
            {
                "id": "ak74-id",
                "name": "AK-74",
                "shortName": "AK74",
                "avg24hPrice": 25000,
                "types": ["weapon", "assault-rifle"]
            },
            {
                "id": "ak74m-id", 
                "name": "AK-74M",
                "shortName": "AK74M",
                "avg24hPrice": 35000,
                "types": ["weapon", "assault-rifle"]
            }
        ]
    
    @pytest.mark.asyncio
    async def test_search_items_success(self, item_tools, mock_search_response):
        """Test successful item search."""
        with patch('src.tools.items.TarkovGraphQLClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.search_items.return_value = mock_search_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            result = await item_tools.handle_search_items({"name": "AK", "limit": 10})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "AK-74" in result[0].text
            assert "AK-74M" in result[0].text
            assert "₽25,000" in result[0].text
    
    @pytest.mark.asyncio
    async def test_search_items_no_results(self, item_tools):
        """Test item search with no results."""
        with patch('src.tools.items.TarkovGraphQLClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.search_items.return_value = []
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            result = await item_tools.handle_search_items({"name": "NonexistentItem"})
            
            assert len(result) == 1
            assert "No items found" in result[0].text
    
    @pytest.mark.asyncio
    async def test_search_items_missing_params(self, item_tools):
        """Test item search with missing parameters."""
        result = await item_tools.handle_search_items({})
        
        assert len(result) == 1
        assert "Error" in result[0].text
        assert "must be provided" in result[0].text
    
    @pytest.mark.asyncio
    async def test_get_item_details_success(self, item_tools):
        """Test successful item details retrieval."""
        mock_item = {
            "id": "ak74-id",
            "name": "AK-74",
            "shortName": "AK74",
            "description": "Soviet assault rifle",
            "weight": 3.3,
            "width": 4,
            "height": 1,
            "basePrice": 20000,
            "avg24hPrice": 25000,
            "low24hPrice": 22000,
            "high24hPrice": 28000,
            "changeLast48h": 2000,
            "changeLast48hPercent": 8.7,
            "types": ["weapon", "assault-rifle"],
            "sellFor": [
                {"source": "Prapor", "priceRUB": 15000}
            ],
            "buyFor": [
                {"source": "Flea Market", "priceRUB": 25000}
            ],
            "wikiLink": "https://escapefromtarkov.fandom.com/wiki/AK-74"
        }
        
        with patch('src.tools.items.TarkovGraphQLClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get_item_by_id.return_value = mock_item
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            result = await item_tools.handle_get_item_details({"item_id": "ak74-id"})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            text = result[0].text
            assert "AK-74" in text
            assert "Soviet assault rifle" in text
            assert "₽25,000" in text
            assert "3.3 kg" in text
            assert "4x1 slots" in text
    
    @pytest.mark.asyncio
    async def test_get_item_details_not_found(self, item_tools):
        """Test item details for non-existent item."""
        with patch('src.tools.items.TarkovGraphQLClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get_item_by_id.return_value = None
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            result = await item_tools.handle_get_item_details({"item_id": "nonexistent"})
            
            assert len(result) == 1
            assert "No item found" in result[0].text

class TestMarketTools:
    """Test market tools functionality."""
    
    @pytest.fixture
    def market_tools(self):
        """Create MarketTools instance."""
        return MarketTools()
    
    @pytest.fixture
    def mock_flea_data(self):
        """Mock flea market data."""
        return [
            {
                "id": "item1",
                "name": "Expensive Item",
                "shortName": "EI",
                "avg24hPrice": 100000,
                "low24hPrice": 95000,
                "high24hPrice": 105000,
                "changeLast48hPercent": 5.2
            },
            {
                "id": "item2",
                "name": "Cheap Item", 
                "shortName": "CI",
                "avg24hPrice": 5000,
                "low24hPrice": 4500,
                "high24hPrice": 5500,
                "changeLast48hPercent": -2.1
            }
        ]
    
    @pytest.mark.asyncio
    async def test_get_flea_market_data_success(self, market_tools, mock_flea_data):
        """Test successful flea market data retrieval."""
        with patch('src.tools.market.TarkovGraphQLClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get_flea_market_data.return_value = mock_flea_data
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            result = await market_tools.handle_get_flea_market_data({"limit": 10})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            text = result[0].text
            assert "Expensive Item" in text
            assert "₽100,000" in text
            assert "+5.2%" in text
            assert "📈" in text  # Positive trend indicator
    
    @pytest.mark.asyncio
    async def test_get_barter_trades_success(self, market_tools):
        """Test successful barter trades retrieval."""
        mock_barters = [
            {
                "id": "barter1",
                "trader": {"name": "Prapor"},
                "level": 2,
                "buyLimit": 5,
                "requiredItems": [
                    {
                        "item": {"id": "item1", "name": "Required Item", "avg24hPrice": 10000},
                        "count": 2
                    }
                ],
                "rewardItems": [
                    {
                        "item": {"id": "item2", "name": "Reward Item", "avg24hPrice": 25000},
                        "count": 1
                    }
                ]
            }
        ]
        
        with patch('src.tools.market.TarkovGraphQLClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get_barters.return_value = mock_barters
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            result = await market_tools.handle_get_barter_trades({"limit": 10})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            text = result[0].text
            assert "Prapor" in text
            assert "Level 2" in text
            assert "Required Item" in text
            assert "Reward Item" in text
            assert "₽5,000" in text  # Profit calculation
            assert "💰" in text  # Profit indicator
    
    @pytest.mark.asyncio
    async def test_calculate_barter_profit_success(self, market_tools):
        """Test successful barter profit calculation."""
        mock_barters = [
            {
                "id": "target-barter",
                "trader": {"name": "Therapist"},
                "level": 1,
                "requiredItems": [
                    {
                        "item": {"id": "item1", "name": "Medicine", "avg24hPrice": 8000},
                        "count": 3
                    }
                ],
                "rewardItems": [
                    {
                        "item": {"id": "item2", "name": "Medkit", "avg24hPrice": 30000},
                        "count": 1
                    }
                ]
            }
        ]
        
        with patch('src.tools.market.TarkovGraphQLClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get_barters.return_value = mock_barters
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            result = await market_tools.handle_calculate_barter_profit({"barter_id": "target-barter"})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            text = result[0].text
            assert "Therapist" in text
            assert "₽24,000" in text  # Total cost (3 * 8000)
            assert "₽30,000" in text  # Total value
            assert "₽6,000" in text   # Profit
            assert "💰 Profitable" in text
    
    @pytest.mark.asyncio
    async def test_calculate_barter_profit_not_found(self, market_tools):
        """Test barter profit calculation for non-existent barter."""
        with patch('src.tools.market.TarkovGraphQLClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get_barters.return_value = []
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            result = await market_tools.handle_calculate_barter_profit({"barter_id": "nonexistent"})
            
            assert len(result) == 1
            assert "No barter found" in result[0].text