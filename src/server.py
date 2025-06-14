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

from .tools.items import ItemTools
from .tools.market import MarketTools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tarkov-mcp-server")

class TarkovMCPServer:
    """Main MCP server class for Tarkov API."""
    
    def __init__(self):
        self.server = Server("tarkov-mcp-server")
        self.item_tools = ItemTools()
        self.market_tools = MarketTools()
        
        # Combine all tools
        self.all_tools = self.item_tools.tools + self.market_tools.tools
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all MCP handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List available tools."""
            return self.all_tools
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            """Handle tool calls."""
            logger.info(f"Tool called: {name} with arguments: {arguments}")
            
            try:
                # Route to appropriate tool handler
                if name == "search_items":
                    return await self.item_tools.handle_search_items(arguments)
                elif name == "get_item_details":
                    return await self.item_tools.handle_get_item_details(arguments)
                elif name == "get_flea_market_data":
                    return await self.market_tools.handle_get_flea_market_data(arguments)
                elif name == "get_barter_trades":
                    return await self.market_tools.handle_get_barter_trades(arguments)
                elif name == "calculate_barter_profit":
                    return await self.market_tools.handle_calculate_barter_profit(arguments)
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