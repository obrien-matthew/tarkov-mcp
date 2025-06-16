"""Main MCP server for Tarkov API."""

import asyncio
import logging
from typing import Any, Sequence
from mcp.server import Server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource,
    LoggingLevel
)
import mcp.server.stdio
import mcp.types as types

from tarkov_mcp.tools.items import ItemTools
from tarkov_mcp.tools.market import MarketTools
from tarkov_mcp.tools.maps import MapTools
from tarkov_mcp.tools.traders import TraderTools
from tarkov_mcp.tools.quests import QuestTools
from tarkov_mcp.tools.community import CommunityTools

# Configure logging
from tarkov_mcp.config import config
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("tarkov-mcp-server")

class TarkovMCPServer:
    """Main MCP server class for Tarkov API."""
    
    def __init__(self):
        self.server = Server("tarkov-mcp-server")
        self.item_tools = ItemTools()
        self.market_tools = MarketTools()
        self.map_tools = MapTools()
        self.trader_tools = TraderTools()
        self.quest_tools = QuestTools()
        self.community_tools = CommunityTools()
        
        # Combine all tools
        self.all_tools = (
            self.item_tools.tools + 
            self.market_tools.tools + 
            self.map_tools.tools + 
            self.trader_tools.tools + 
            self.quest_tools.tools +
            self.community_tools.tools
        )
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all MCP handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List available tools."""
            return self.all_tools
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict[str, Any]) -> Sequence[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            """Handle tool calls."""
            logger.info(f"Tool called: {name} with arguments: {arguments}")
            
            try:
                # Route to appropriate tool handler
                if name == "search_items":
                    return await self.item_tools.handle_search_items(arguments)
                elif name == "get_item_details":
                    return await self.item_tools.handle_get_item_details(arguments)
                elif name == "get_item_prices":
                    return await self.item_tools.handle_get_item_prices(arguments)
                elif name == "compare_items":
                    return await self.item_tools.handle_compare_items(arguments)
                elif name == "get_flea_market_data":
                    return await self.market_tools.handle_get_flea_market_data(arguments)
                elif name == "get_barter_trades":
                    return await self.market_tools.handle_get_barter_trades(arguments)
                elif name == "calculate_barter_profit":
                    return await self.market_tools.handle_calculate_barter_profit(arguments)
                elif name == "get_ammo_data":
                    return await self.market_tools.handle_get_ammo_data(arguments)
                elif name == "get_hideout_modules":
                    return await self.market_tools.handle_get_hideout_modules(arguments)
                elif name == "get_crafts":
                    return await self.market_tools.handle_get_crafts(arguments)
                elif name == "get_maps":
                    return await self.map_tools.handle_get_maps(arguments)
                elif name == "get_map_details":
                    return await self.map_tools.handle_get_map_details(arguments)
                elif name == "get_map_spawns":
                    return await self.map_tools.handle_get_map_spawns(arguments)
                elif name == "get_traders":
                    return await self.trader_tools.handle_get_traders(arguments)
                elif name == "get_trader_details":
                    return await self.trader_tools.handle_get_trader_details(arguments)
                elif name == "get_trader_items":
                    return await self.trader_tools.handle_get_trader_items(arguments)
                elif name == "get_quests":
                    return await self.quest_tools.handle_get_quests(arguments)
                elif name == "get_quest_details":
                    return await self.quest_tools.handle_get_quest_details(arguments)
                elif name == "search_quests":
                    return await self.quest_tools.handle_search_quests(arguments)
                elif name == "get_quest_items":
                    return await self.item_tools.handle_get_quest_items(arguments)
                elif name == "get_goon_reports":
                    return await self.community_tools.handle_get_goon_reports(arguments)
                else:
                    return [TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
            except Exception as e:
                logger.error(f"Error handling tool {name}: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error executing tool {name}: {str(e)}"
                )]
    
    async def run(self):
        """Run the MCP server."""
        logger.info("Starting Tarkov MCP Server...")
        
        # Run the server using stdio transport
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

async def main():
    """Main entry point."""
    server = TarkovMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
