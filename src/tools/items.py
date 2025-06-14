"""Item-related MCP tools."""

from typing import List, Dict, Any
from mcp.types import Tool, TextContent
import logging

from graphql_client import TarkovGraphQLClient

logger = logging.getLogger(__name__)

class ItemTools:
    """Item-related tools for the MCP server."""
    
    def __init__(self):
        self.tools = [
            Tool(
                name="search_items",
                description="Search for Tarkov items by name or type",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Item name to search for (partial matches allowed)"
                        },
                        "item_type": {
                            "type": "string",
                            "description": "Item type to filter by (e.g., 'weapon', 'armor', 'ammo')"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 20,
                            "minimum": 1,
                            "maximum": 100
                        }
                    }
                }
            ),
            Tool(
                name="get_item_details",
                description="Get detailed information about a specific item by ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "item_id": {
                            "type": "string",
                            "description": "The unique ID of the item"
                        }
                    },
                    "required": ["item_id"]
                }
            )
        ]
    
    async def handle_search_items(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle search_items tool call."""
        name = arguments.get("name")
        item_type = arguments.get("item_type")
        limit = arguments.get("limit", 20)
        
        if not name and not item_type:
            return [TextContent(
                type="text",
                text="Error: Either 'name' or 'item_type' must be provided"
            )]
        
        try:
            async with TarkovGraphQLClient() as client:
                items = await client.search_items(name=name, item_type=item_type, limit=limit)
            
            if not items:
                return [TextContent(
                    type="text",
                    text="No items found matching the search criteria"
                )]
            
            # Format results
            result_text = f"Found {len(items)} items:\n\n"
            for item in items:
                price_info = ""
                if item.get("avg24hPrice"):
                    price_info = f" (₽{item['avg24hPrice']:,})"
                
                result_text += f"• **{item['name']}** ({item['shortName']}){price_info}\n"
                result_text += f"  ID: {item['id']}\n"
                if item.get("types"):
                    result_text += f"  Types: {', '.join(item['types'])}\n"
                result_text += "\n"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"Error searching items: {e}")
            return [TextContent(
                type="text",
                text=f"Error searching items: {str(e)}"
            )]
    
    async def handle_get_item_details(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get_item_details tool call."""
        item_id = arguments.get("item_id")
        
        if not item_id:
            return [TextContent(
                type="text",
                text="Error: 'item_id' is required"
            )]
        
        try:
            async with TarkovGraphQLClient() as client:
                item = await client.get_item_by_id(item_id)
            
            if not item:
                return [TextContent(
                    type="text",
                    text=f"No item found with ID: {item_id}"
                )]
            
            # Format detailed item information
            result_text = f"# {item['name']} ({item['shortName']})\n\n"
            
            if item.get("description"):
                result_text += f"**Description:** {item['description']}\n\n"
            
            # Basic properties
            result_text += "## Properties\n"
            result_text += f"• **ID:** {item['id']}\n"
            result_text += f"• **Weight:** {item.get('weight', 'N/A')} kg\n"
            result_text += f"• **Size:** {item.get('width', 'N/A')}x{item.get('height', 'N/A')} slots\n"
            result_text += f"• **Base Price:** ₽{item.get('basePrice', 0):,}\n"
            
            if item.get("types"):
                result_text += f"• **Types:** {', '.join(item['types'])}\n"
            
            # Price information
            if item.get("avg24hPrice"):
                result_text += f"\n## Market Prices\n"
                result_text += f"• **24h Average:** ₽{item['avg24hPrice']:,}\n"
                
                if item.get("low24hPrice"):
                    result_text += f"• **24h Low:** ₽{item['low24hPrice']:,}\n"
                if item.get("high24hPrice"):
                    result_text += f"• **24h High:** ₽{item['high24hPrice']:,}\n"
                if item.get("changeLast48h"):
                    change_percent = item.get("changeLast48hPercent", 0)
                    result_text += f"• **48h Change:** ₽{item['changeLast48h']:,} ({change_percent:+.1f}%)\n"
            
            # Sell prices
            if item.get("sellFor"):
                result_text += f"\n## Sell Prices\n"
                for sell_option in item["sellFor"]:
                    source = sell_option.get("source", "Unknown")
                    price = sell_option.get("priceRUB", 0)
                    result_text += f"• **{source}:** ₽{price:,}\n"
            
            # Buy prices
            if item.get("buyFor"):
                result_text += f"\n## Buy Prices\n"
                for buy_option in item["buyFor"]:
                    source = buy_option.get("source", "Unknown")
                    price = buy_option.get("priceRUB", 0)
                    result_text += f"• **{source}:** ₽{price:,}\n"
            
            # Quest usage
            if item.get("usedInTasks"):
                result_text += f"\n## Used in Quests\n"
                for task in item["usedInTasks"]:
                    trader = task.get("trader", {}).get("name", "Unknown")
                    result_text += f"• **{task['name']}** (from {trader})\n"
            
            # Links
            if item.get("wikiLink"):
                result_text += f"\n**Wiki:** {item['wikiLink']}\n"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"Error getting item details: {e}")
            return [TextContent(
                type="text",
                text=f"Error getting item details: {str(e)}"
            )]