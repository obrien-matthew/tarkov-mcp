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

    @pytest.mark.asyncio
    async def test_get_ammo_data_success(self, market_tools):
        """Test get_ammo_data with successful response."""
        mock_ammo_data = [
            {
                "item": {"name": "M855A1", "avg24hPrice": 500},
                "caliber": "5.56x45mm",
                "damage": 43,
                "penetrationPower": 37,
                "armorDamage": 37
            },
            {
                "item": {"name": "M995", "avg24hPrice": 1200},
                "caliber": "5.56x45mm", 
                "damage": 40,
                "penetrationPower": 53,
                "armorDamage": 38
            }
        ]
        
        with patch('src.tools.market.TarkovGraphQLClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_ammo_data.return_value = mock_ammo_data
            
            result = await market_tools.handle_get_ammo_data({"caliber": "5.56x45mm"})
            
            assert len(result) == 1
            assert "5.56x45mm" in result[0].text
            assert "M855A1" in result[0].text
            assert "M995" in result[0].text

    @pytest.mark.asyncio
    async def test_get_hideout_modules_success(self, market_tools):
        """Test get_hideout_modules with successful response."""
        mock_modules = [
            {
                "name": "Workbench",
                "level": 1,
                "require": [
                    {"item": {"name": "Screws"}, "count": 5}
                ],
                "bonuses": [
                    {"type": "CraftingSpeed", "value": 10}
                ]
            }
        ]
        
        with patch('src.tools.market.TarkovGraphQLClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_hideout_modules.return_value = mock_modules
            
            result = await market_tools.handle_get_hideout_modules({})
            
            assert len(result) == 1
            assert "Workbench" in result[0].text
            assert "Level 1" in result[0].text


class TestItemToolsExtended:
    """Test extended item tools functionality."""
    
    @pytest.fixture
    def item_tools(self):
        """Create ItemTools instance."""
        return ItemTools()

    @pytest.mark.asyncio
    async def test_get_item_prices_success(self, item_tools):
        """Test get_item_prices with successful response."""
        mock_items = [
            {
                "name": "AK-74",
                "avg24hPrice": 25000,
                "low24hPrice": 20000,
                "high24hPrice": 30000,
                "changeLast48hPercent": 5.2
            }
        ]
        
        with patch('src.tools.items.TarkovGraphQLClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.search_items.return_value = mock_items
            
            result = await item_tools.handle_get_item_prices({"item_names": ["AK-74"]})
            
            assert len(result) == 1
            assert "AK-74" in result[0].text
            assert "₽25,000" in result[0].text
            assert "+5.2%" in result[0].text

    @pytest.mark.asyncio
    async def test_compare_items_success(self, item_tools):
        """Test compare_items with successful response."""
        mock_items = [
            {
                "id": "item1",
                "name": "AK-74",
                "weight": 3.2,
                "width": 4,
                "height": 1,
                "basePrice": 20000,
                "avg24hPrice": 25000
            },
            {
                "id": "item2", 
                "name": "M4A1",
                "weight": 3.4,
                "width": 4,
                "height": 1,
                "basePrice": 35000,
                "avg24hPrice": 40000
            }
        ]
        
        with patch('src.tools.items.TarkovGraphQLClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_item_by_id.side_effect = mock_items
            
            result = await item_tools.handle_compare_items({"item_ids": ["item1", "item2"]})
            
            assert len(result) == 1
            assert "AK-74" in result[0].text
            assert "M4A1" in result[0].text
            assert "Basic Information" in result[0].text
            assert "Market Prices" in result[0].text

    @pytest.mark.asyncio
    async def test_compare_items_insufficient_items(self, item_tools):
        """Test compare_items with insufficient items."""
        result = await item_tools.handle_compare_items({"item_ids": ["item1"]})
        
        assert len(result) == 1
        assert "At least 2 item IDs are required" in result[0].text


class TestMapTools:
    """Test map tools functionality."""
    
    @pytest.fixture
    def map_tools(self):
        """Create MapTools instance for testing."""
        return MapTools()
    
    @pytest.fixture
    def mock_maps_data(self):
        """Mock maps data for testing."""
        return [
            {
                "name": "Customs",
                "description": "Industrial area",
                "raidDuration": 35,
                "players": "8-12",
                "bosses": [
                    {"name": "Reshala", "spawnChance": 35}
                ]
            },
            {
                "name": "Factory",
                "description": "Close quarters combat",
                "raidDuration": 20,
                "players": "4-6",
                "bosses": []
            }
        ]
    
    @pytest.mark.asyncio
    async def test_get_maps_success(self, map_tools, mock_maps_data):
        """Test get_maps with successful response."""
        with patch('src.tools.maps.TarkovGraphQLClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_maps.return_value = mock_maps_data
            
            result = await map_tools.handle_get_maps({})
            
            assert len(result) == 1
            assert "Customs" in result[0].text
            assert "Factory" in result[0].text
            assert "35 minutes" in result[0].text

    @pytest.mark.asyncio
    async def test_get_map_details_success(self, map_tools):
        """Test get_map_details with successful response."""
        mock_map_data = {
            "name": "Customs",
            "description": "Industrial area",
            "raidDuration": 35,
            "players": "8-12",
            "extracts": [
                {"name": "Crossroads", "faction": "Any"}
            ],
            "bosses": [
                {
                    "name": "Reshala",
                    "spawnChance": 35,
                    "spawnLocations": [
                        {"name": "Gas Station", "chance": 40}
                    ]
                }
            ]
        }
        
        with patch('src.tools.maps.TarkovGraphQLClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_map_by_name.return_value = mock_map_data
            
            result = await map_tools.handle_get_map_details({"map_name": "Customs"})
            
            assert len(result) == 1
            assert "Customs" in result[0].text
            assert "Reshala" in result[0].text
            assert "Crossroads" in result[0].text

    @pytest.mark.asyncio
    async def test_get_map_details_not_found(self, map_tools):
        """Test get_map_details with non-existent map."""
        with patch('src.tools.maps.TarkovGraphQLClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_map_by_name.return_value = None
            
            result = await map_tools.handle_get_map_details({"map_name": "NonExistent"})
            
            assert len(result) == 1
            assert "No map found" in result[0].text

    @pytest.mark.asyncio
    async def test_get_map_spawns_success(self, map_tools):
        """Test get_map_spawns with successful response."""
        mock_map_data = {
            "name": "Customs",
            "bosses": [
                {
                    "name": "Reshala",
                    "spawnChance": 35,
                    "spawnLocations": [
                        {"name": "Gas Station", "chance": 40}
                    ],
                    "escorts": [
                        {
                            "name": "Reshala Guard",
                            "amount": [{"min": 2, "max": 4}]
                        }
                    ]
                }
            ]
        }
        
        with patch('src.tools.maps.TarkovGraphQLClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_map_by_name.return_value = mock_map_data
            
            result = await map_tools.handle_get_map_spawns({"map_name": "Customs"})
            
            assert len(result) == 1
            assert "Reshala" in result[0].text
            assert "Gas Station" in result[0].text


class TestTraderTools:
    """Test trader tools functionality."""
    
    @pytest.fixture
    def trader_tools(self):
        """Create TraderTools instance for testing."""
        return TraderTools()
    
    @pytest.fixture
    def mock_traders_data(self):
        """Mock traders data for testing."""
        return [
            {
                "name": "Prapor",
                "description": "Military equipment dealer",
                "location": "Tarkov",
                "resetTime": 3,
                "currency": [{"name": "RUB"}]
            },
            {
                "name": "Therapist",
                "description": "Medical supplies",
                "location": "Tarkov",
                "resetTime": 3,
                "currency": [{"name": "RUB"}, {"name": "USD"}]
            }
        ]
    
    @pytest.mark.asyncio
    async def test_get_traders_success(self, trader_tools, mock_traders_data):
        """Test get_traders with successful response."""
        with patch('src.tools.traders.TarkovGraphQLClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_traders.return_value = mock_traders_data
            
            result = await trader_tools.handle_get_traders({})
            
            assert len(result) == 1
            assert "Prapor" in result[0].text
            assert "Therapist" in result[0].text
            assert "3 hours" in result[0].text

    @pytest.mark.asyncio
    async def test_get_trader_details_success(self, trader_tools):
        """Test get_trader_details with successful response."""
        mock_trader_data = {
            "name": "Prapor",
            "description": "Military equipment dealer",
            "location": "Tarkov",
            "resetTime": 3,
            "currency": [{"name": "RUB"}],
            "levels": [
                {
                    "level": 1,
                    "requiredPlayerLevel": 1,
                    "requiredReputation": 0.0,
                    "requiredCommerce": 0
                }
            ],
            "insurance": {
                "availableOnMap": True,
                "minReturnHour": 12,
                "maxReturnHour": 36
            }
        }
        
        with patch('src.tools.traders.TarkovGraphQLClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_trader_by_name.return_value = mock_trader_data
            
            result = await trader_tools.handle_get_trader_details({"trader_name": "Prapor"})
            
            assert len(result) == 1
            assert "Prapor" in result[0].text
            assert "Insurance" in result[0].text
            assert "Level 1" in result[0].text

    @pytest.mark.asyncio
    async def test_get_trader_items_success(self, trader_tools):
        """Test get_trader_items with successful response."""
        mock_items = [
            {
                "item": {
                    "name": "AK-74",
                    "types": ["AssaultRifle"]
                },
                "priceRUB": 25000,
                "currency": "RUB",
                "minTraderLevel": 1
            }
        ]
        
        with patch('src.tools.traders.TarkovGraphQLClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_trader_items.return_value = mock_items
            
            result = await trader_tools.handle_get_trader_items({"trader_name": "Prapor"})
            
            assert len(result) == 1
            assert "AK-74" in result[0].text
            assert "25,000 RUB" in result[0].text

    @pytest.mark.asyncio
    async def test_get_trader_details_not_found(self, trader_tools):
        """Test get_trader_details with non-existent trader."""
        with patch('src.tools.traders.TarkovGraphQLClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_trader_by_name.return_value = None
            
            result = await trader_tools.handle_get_trader_details({"trader_name": "NonExistent"})
            
            assert len(result) == 1
            assert "No trader found" in result[0].text


class TestQuestTools:
    """Test quest tools functionality."""
    
    @pytest.fixture
    def quest_tools(self):
        """Create QuestTools instance for testing."""
        return QuestTools()
    
    @pytest.fixture
    def mock_quests_data(self):
        """Mock quests data for testing."""
        return [
            {
                "id": "quest1",
                "name": "Debut",
                "trader": {"name": "Prapor"},
                "minPlayerLevel": 1,
                "experience": 1000,
                "taskRequirements": []
            },
            {
                "id": "quest2", 
                "name": "Checking",
                "trader": {"name": "Prapor"},
                "minPlayerLevel": 2,
                "experience": 1500,
                "taskRequirements": [
                    {"task": {"name": "Debut"}}
                ]
            }
        ]
    
    @pytest.mark.asyncio
    async def test_get_quests_success(self, quest_tools, mock_quests_data):
        """Test get_quests with successful response."""
        with patch('src.tools.quests.TarkovGraphQLClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_quests.return_value = mock_quests_data
            
            result = await quest_tools.handle_get_quests({})
            
            assert len(result) == 1
            assert "Debut" in result[0].text
            assert "Checking" in result[0].text
            assert "Prapor" in result[0].text

    @pytest.mark.asyncio
    async def test_get_quest_details_success(self, quest_tools):
        """Test get_quest_details with successful response."""
        mock_quest_data = {
            "id": "quest1",
            "name": "Debut",
            "description": "Eliminate scavs on Customs",
            "trader": {"name": "Prapor"},
            "minPlayerLevel": 1,
            "experience": 1000,
            "objectives": [
                {
                    "description": "Eliminate 5 Scavs on Customs",
                    "maps": [{"name": "Customs"}]
                }
            ],
            "finishRewards": {
                "items": [
                    {"item": {"name": "AK-74U"}, "count": 1}
                ]
            }
        }
        
        with patch('src.tools.quests.TarkovGraphQLClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_quest_by_id.return_value = mock_quest_data
            
            result = await quest_tools.handle_get_quest_details({"quest_id": "quest1"})
            
            assert len(result) == 1
            assert "Debut" in result[0].text
            assert "Eliminate 5 Scavs" in result[0].text
            assert "AK-74U" in result[0].text

    @pytest.mark.asyncio
    async def test_search_quests_success(self, quest_tools):
        """Test search_quests with successful response."""
        mock_search_results = [
            {
                "id": "quest1",
                "name": "Debut",
                "description": "Eliminate scavs on Customs",
                "trader": {"name": "Prapor"},
                "minPlayerLevel": 1,
                "experience": 1000
            }
        ]
        
        with patch('src.tools.quests.TarkovGraphQLClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.search_quests.return_value = mock_search_results
            
            result = await quest_tools.handle_search_quests({"query": "debut"})
            
            assert len(result) == 1
            assert "Debut" in result[0].text
            assert "Prapor" in result[0].text

    @pytest.mark.asyncio
    async def test_search_quests_no_results(self, quest_tools):
        """Test search_quests with no results."""
        with patch('src.tools.quests.TarkovGraphQLClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.search_quests.return_value = []
            
            result = await quest_tools.handle_search_quests({"query": "nonexistent"})
            
            assert len(result) == 1
            assert "No quests found" in result[0].text

    @pytest.mark.asyncio
    async def test_get_quest_details_not_found(self, quest_tools):
        """Test get_quest_details with non-existent quest."""
        with patch('src.tools.quests.TarkovGraphQLClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_quest_by_id.return_value = None
            
            result = await quest_tools.handle_get_quest_details({"quest_id": "nonexistent"})
            
            assert len(result) == 1
            assert "No quest found" in result[0].text
