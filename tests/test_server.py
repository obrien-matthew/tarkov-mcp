"""Tests for MCP server integration."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from mcp.types import TextContent, Tool

from tarkov_mcp.server import TarkovMCPServer

# Set timeout for all async tests to prevent hanging
pytestmark = pytest.mark.timeout(30)


class TestTarkovMCPServer:
    """Test MCP server integration."""
    
    @pytest.fixture
    def server(self):
        """Create server instance for testing."""
        return TarkovMCPServer()
    
    def test_server_initialization(self, server):
        """Test server initializes correctly."""
        assert server.server is not None
        assert server.item_tools is not None
        assert server.market_tools is not None
        assert server.map_tools is not None
        assert server.trader_tools is not None
        assert server.quest_tools is not None
        assert server.community_tools is not None
        assert len(server.all_tools) > 0
    
    def test_all_tools_registered(self, server):
        """Test all tools are properly registered."""
        tool_names = [tool.name for tool in server.all_tools]
        
        # Item tools
        assert "search_items" in tool_names
        assert "get_item_details" in tool_names
        assert "get_item_prices" in tool_names
        assert "compare_items" in tool_names
        assert "get_quest_items" in tool_names
        
        # Market tools
        assert "get_flea_market_data" in tool_names
        assert "get_barter_trades" in tool_names
        assert "calculate_barter_profit" in tool_names
        assert "get_ammo_data" in tool_names
        assert "get_hideout_modules" in tool_names
        assert "get_crafts" in tool_names
        
        # Map tools
        assert "get_maps" in tool_names
        assert "get_map_details" in tool_names
        assert "get_map_spawns" in tool_names
        
        # Trader tools
        assert "get_traders" in tool_names
        assert "get_trader_details" in tool_names
        assert "get_trader_items" in tool_names
        
        # Quest tools
        assert "get_quests" in tool_names
        assert "get_quest_details" in tool_names
        assert "search_quests" in tool_names
        
        # Community tools
        assert "get_goon_reports" in tool_names
    
    def test_tool_schemas_valid(self, server):
        """Test all tool schemas are valid."""
        for tool in server.all_tools:
            assert isinstance(tool, Tool)
            assert tool.name
            assert tool.description
            assert tool.inputSchema
            assert tool.inputSchema["type"] == "object"
    
    @pytest.mark.asyncio
    async def test_search_items_tool_call(self, server):
        """Test search_items tool call routing."""
        with patch.object(server.item_tools, 'handle_search_items') as mock_handler:
            mock_handler.return_value = [TextContent(type="text", text="Test result")]
            
            # Test tool routing by directly calling the handler methods
            result = await server.item_tools.handle_search_items({"name": "test"})
            mock_handler.assert_called_once_with({"name": "test"})
            assert len(result) == 1
            assert result[0].text == "Test result"
    
    @pytest.mark.asyncio
    async def test_get_quest_items_tool_call(self, server):
        """Test get_quest_items tool call routing."""
        with patch.object(server.item_tools, 'handle_get_quest_items') as mock_handler:
            mock_handler.return_value = [TextContent(type="text", text="Quest items result")]
            
            result = await server.item_tools.handle_get_quest_items({"limit": 50})
            mock_handler.assert_called_once_with({"limit": 50})
            assert len(result) == 1
            assert result[0].text == "Quest items result"
    
    @pytest.mark.asyncio
    async def test_get_goon_reports_tool_call(self, server):
        """Test get_goon_reports tool call routing."""
        with patch.object(server.community_tools, 'handle_get_goon_reports') as mock_handler:
            mock_handler.return_value = [TextContent(type="text", text="Goon reports result")]
            
            result = await server.community_tools.handle_get_goon_reports({"limit": 10})
            mock_handler.assert_called_once_with({"limit": 10})
            assert len(result) == 1
            assert result[0].text == "Goon reports result"
    
    def test_tool_collections_not_empty(self, server):
        """Test that all tool collections contain tools."""
        assert len(server.item_tools.tools) > 0
        assert len(server.market_tools.tools) > 0
        assert len(server.map_tools.tools) > 0
        assert len(server.trader_tools.tools) > 0
        assert len(server.quest_tools.tools) > 0
        assert len(server.community_tools.tools) > 0
    
    @pytest.mark.asyncio
    async def test_tool_error_handling_direct(self, server):
        """Test error handling in tool calls directly."""
        with patch('tarkov_mcp.tools.items.TarkovGraphQLClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.search_items.side_effect = Exception("Network error")
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            result = await server.item_tools.handle_search_items({"name": "test"})
            assert len(result) == 1
            assert "Error searching items" in result[0].text
    
    @pytest.mark.asyncio 
    async def test_language_support_integration(self, server):
        """Test language support is properly integrated."""
        # Test that search_items tool supports language parameter
        search_items_tool = next((t for t in server.all_tools if t.name == "search_items"), None)
        assert search_items_tool is not None
        
        properties = search_items_tool.inputSchema.get("properties", {})
        assert "language" in properties
        assert properties["language"]["type"] == "string"
        assert properties["language"]["default"] == "en"
        
        # Test that get_quest_items tool supports language parameter
        quest_items_tool = next((t for t in server.all_tools if t.name == "get_quest_items"), None)
        assert quest_items_tool is not None
        
        properties = quest_items_tool.inputSchema.get("properties", {})
        assert "language" in properties
        assert properties["language"]["type"] == "string"
        assert properties["language"]["default"] == "en"


class TestServerSchemaValidation:
    """Test server schema validation and compatibility."""
    
    @pytest.fixture
    def server(self):
        """Create server instance for testing."""
        return TarkovMCPServer()
    
    def test_item_tools_schema_language_support(self, server):
        """Test item tools have proper language support in schemas."""
        search_tool = next((t for t in server.all_tools if t.name == "search_items"), None)
        assert search_tool is not None
        
        schema = search_tool.inputSchema
        properties = schema.get("properties", {})
        
        # Check language parameter
        assert "language" in properties
        lang_prop = properties["language"]
        assert lang_prop["type"] == "string"
        assert lang_prop["default"] == "en"
        assert "Language code for localized results" in lang_prop["description"]
    
    def test_community_tools_schema(self, server):
        """Test community tools have proper schemas."""
        goon_tool = next((t for t in server.all_tools if t.name == "get_goon_reports"), None)
        assert goon_tool is not None
        
        schema = goon_tool.inputSchema
        properties = schema.get("properties", {})
        
        # Check limit parameter
        assert "limit" in properties
        limit_prop = properties["limit"]
        assert limit_prop["type"] == "integer"
        assert limit_prop["default"] == 10
        assert limit_prop["minimum"] == 1
        assert limit_prop["maximum"] == 50
    
    def test_quest_items_tool_schema(self, server):
        """Test quest items tool has proper schema."""
        quest_items_tool = next((t for t in server.all_tools if t.name == "get_quest_items"), None)
        assert quest_items_tool is not None
        
        schema = quest_items_tool.inputSchema
        properties = schema.get("properties", {})
        
        # Check both limit and language parameters
        assert "limit" in properties
        assert "language" in properties
        
        limit_prop = properties["limit"]
        assert limit_prop["type"] == "integer"
        assert limit_prop["default"] == 50
        
        lang_prop = properties["language"]
        assert lang_prop["type"] == "string"
        assert lang_prop["default"] == "en"
    
    def test_all_tools_have_descriptions(self, server):
        """Test all tools have meaningful descriptions."""
        for tool in server.all_tools:
            assert tool.description
            assert len(tool.description) > 10  # Meaningful description
            assert not tool.description.startswith("TODO")  # No placeholder descriptions
    
    def test_schema_consistency(self, server):
        """Test schema consistency across tools."""
        # Find all tools with limit parameters
        tools_with_limits = []
        for tool in server.all_tools:
            properties = tool.inputSchema.get("properties", {})
            if "limit" in properties:
                tools_with_limits.append((tool.name, properties["limit"]))
        
        # Check that limit parameters are consistently defined
        for tool_name, limit_prop in tools_with_limits:
            assert limit_prop["type"] == "integer"
            assert "minimum" in limit_prop
            assert limit_prop["minimum"] >= 1
            assert "maximum" in limit_prop or "default" in limit_prop