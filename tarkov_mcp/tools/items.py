"""Item-related MCP tools."""

from typing import List, Dict, Any
from mcp.types import Tool, TextContent
import logging

from tarkov_mcp.graphql_client import TarkovGraphQLClient

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
            ),
            Tool(
                name="get_item_prices",
                description="Get current market prices for multiple items",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "item_names": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of item names to get prices for"
                        }
                    },
                    "required": ["item_names"]
                }
            ),
            Tool(
                name="compare_items",
                description="Compare stats and prices between multiple items",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "item_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of item IDs to compare"
                        }
                    },
                    "required": ["item_ids"]
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
            logger.error(f"Error searching items: {e}", exc_info=True)
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
            logger.error(f"Error getting item details: {e}", exc_info=True)
            return [TextContent(
                type="text",
                text=f"Error getting item details: {str(e)}"
            )]
    
    async def handle_get_item_prices(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get_item_prices tool call."""
        item_names = arguments.get("item_names", [])
        
        if not item_names:
            return [TextContent(
                type="text",
                text="Error: 'item_names' list is required"
            )]
        
        try:
            async with TarkovGraphQLClient() as client:
                all_prices = []
                
                for item_name in item_names:
                    items = await client.search_items(name=item_name, limit=1)
                    if items:
                        all_prices.append(items[0])
                    else:
                        all_prices.append({"name": item_name, "error": "Not found"})
            
            result_text = f"# Item Prices ({len(item_names)} requested)\n\n"
            
            for item in all_prices:
                if item.get("error"):
                    result_text += f"• **{item['name']}**: {item['error']}\n"
                else:
                    name = item.get("name", "Unknown")
                    avg_price = item.get("avg24hPrice", 0)
                    low_price = item.get("low24hPrice", 0)
                    high_price = item.get("high24hPrice", 0)
                    change_48h = item.get("changeLast48hPercent", 0)
                    
                    result_text += f"• **{name}**\n"
                    if avg_price > 0:
                        result_text += f"  - Average: ₽{avg_price:,}\n"
                        if low_price and high_price:
                            result_text += f"  - Range: ₽{low_price:,} - ₽{high_price:,}\n"
                        if change_48h != 0:
                            trend = "📈" if change_48h > 0 else "📉"
                            result_text += f"  - 48h Change: {change_48h:+.1f}% {trend}\n"
                    else:
                        result_text += f"  - No price data available\n"
                
                result_text += "\n"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"Error getting item prices: {e}")
            return [TextContent(
                type="text",
                text=f"Error getting item prices: {str(e)}"
            )]
    
    async def handle_compare_items(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle compare_items tool call."""
        item_ids = arguments.get("item_ids", [])
        
        if not item_ids or len(item_ids) < 2:
            return [TextContent(
                type="text",
                text="Error: At least 2 item IDs are required for comparison"
            )]
        
        try:
            async with TarkovGraphQLClient() as client:
                items = []
                for item_id in item_ids:
                    item = await client.get_item_by_id(item_id)
                    if item:
                        items.append(item)
                    else:
                        items.append({"id": item_id, "error": "Not found"})
            
            result_text = f"# Item Comparison ({len(items)} items)\n\n"
            
            # Basic info comparison
            result_text += "## Basic Information\n"
            result_text += "| Item | Weight | Size | Base Price |\n"
            result_text += "|------|--------|------|------------|\n"
            
            for item in items:
                if item.get("error"):
                    result_text += f"| {item['id']} | Error: {item['error']} | - | - |\n"
                else:
                    name = item.get("name", "Unknown")
                    weight = item.get("weight", 0)
                    width = item.get("width", 0)
                    height = item.get("height", 0)
                    base_price = item.get("basePrice", 0)
                    
                    result_text += f"| {name} | {weight}kg | {width}x{height} | ₽{base_price:,} |\n"
            
            # Market prices comparison
            result_text += "\n## Market Prices\n"
            result_text += "| Item | 24h Average | 24h Low | 24h High | 48h Change |\n"
            result_text += "|------|-------------|---------|----------|------------|\n"
            
            for item in items:
                if not item.get("error"):
                    name = item.get("name", "Unknown")
                    avg_price = item.get("avg24hPrice", 0)
                    low_price = item.get("low24hPrice", 0)
                    high_price = item.get("high24hPrice", 0)
                    change_48h = item.get("changeLast48hPercent", 0)
                    
                    avg_text = f"₽{avg_price:,}" if avg_price > 0 else "N/A"
                    low_text = f"₽{low_price:,}" if low_price > 0 else "N/A"
                    high_text = f"₽{high_price:,}" if high_price > 0 else "N/A"
                    change_text = f"{change_48h:+.1f}%" if change_48h != 0 else "0%"
                    
                    result_text += f"| {name} | {avg_text} | {low_text} | {high_text} | {change_text} |\n"
            
            # Value analysis
            valid_items = [item for item in items if not item.get("error") and item.get("avg24hPrice", 0) > 0]
            if len(valid_items) > 1:
                result_text += "\n## Value Analysis\n"
                
                # Price per slot
                result_text += "### Price per Inventory Slot\n"
                for item in valid_items:
                    name = item.get("name", "Unknown")
                    avg_price = item.get("avg24hPrice", 0)
                    width = item.get("width", 1)
                    height = item.get("height", 1)
                    slots = width * height
                    price_per_slot = avg_price / slots if slots > 0 else 0
                    
                    result_text += f"• **{name}**: ₽{price_per_slot:,.0f} per slot\n"
                
                # Best value
                best_value_item = max(valid_items, key=lambda x: x.get("avg24hPrice", 0) / (x.get("width", 1) * x.get("height", 1)))
                result_text += f"\n**Best Value:** {best_value_item.get('name', 'Unknown')}\n"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"Error comparing items: {e}")
            return [TextContent(
                type="text",
                text=f"Error comparing items: {str(e)}"
            )]
