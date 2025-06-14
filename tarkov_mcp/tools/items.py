"""Item-related MCP tools."""

from typing import List, Dict, Any
from mcp.types import Tool, TextContent
import logging

from tarkov_mcp.graphql_client import TarkovGraphQLClient
from tarkov_mcp.schema import Item, parse_item_from_api

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
                items_data = await client.search_items(name=name, item_type=item_type, limit=limit)
            
            if not items_data:
                return [TextContent(
                    type="text",
                    text="No items found matching the search criteria"
                )]
            
            # Parse items using schema
            items = [parse_item_from_api(item_data) for item_data in items_data]
            
            # Format results
            result_text = f"Found {len(items)} items:\n\n"
            for item in items:
                price_info = ""
                if item.avg24h_price:
                    price_info = f" (₽{item.avg24h_price:,})"
                
                short_name = item.short_name or ""
                result_text += f"• **{item.name}** ({short_name}){price_info}\n"
                result_text += f"  ID: {item.id}\n"
                if item.types:
                    result_text += f"  Types: {', '.join(item.types)}\n"
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
                item_data = await client.get_item_by_id(item_id)
            
            if not item_data:
                return [TextContent(
                    type="text",
                    text=f"No item found with ID: {item_id}"
                )]
            
            # Parse item using schema
            item = parse_item_from_api(item_data)
            
            # Format detailed item information
            short_name = item.short_name or ""
            result_text = f"# {item.name} ({short_name})\n\n"
            
            if item.description:
                result_text += f"**Description:** {item.description}\n\n"
            
            # Basic properties
            result_text += "## Properties\n"
            result_text += f"• **ID:** {item.id}\n"
            result_text += f"• **Weight:** {item.weight or 'N/A'} kg\n"
            # Note: width/height not in schema, using raw data for now
            width = item_data.get('width', 'N/A')
            height = item_data.get('height', 'N/A')
            result_text += f"• **Size:** {width}x{height} slots\n"
            result_text += f"• **Base Price:** ₽{item.base_price or 0:,}\n"
            
            if item.types:
                result_text += f"• **Types:** {', '.join(item.types)}\n"
            
            # Price information
            if item.avg24h_price:
                result_text += f"\n## Market Prices\n"
                result_text += f"• **24h Average:** ₽{item.avg24h_price:,}\n"
                
                if item.low24h_price:
                    result_text += f"• **24h Low:** ₽{item.low24h_price:,}\n"
                if item.high24h_price:
                    result_text += f"• **24h High:** ₽{item.high24h_price:,}\n"
                if item.change_last48h:
                    change_percent = item.change_last48h_percent or 0
                    result_text += f"• **48h Change:** ₽{item.change_last48h:,} ({change_percent:+.1f}%)\n"
            
            # Sell prices
            if item_data.get("sellFor"):
                result_text += f"\n## Sell Prices\n"
                for sell_option in item_data["sellFor"]:
                    source = sell_option.get("source", "Unknown")
                    price = sell_option.get("priceRUB", 0)
                    result_text += f"• **{source}:** ₽{price:,}\n"
            
            # Buy prices
            if item_data.get("buyFor"):
                result_text += f"\n## Buy Prices\n"
                for buy_option in item_data["buyFor"]:
                    source = buy_option.get("source", "Unknown")
                    price = buy_option.get("priceRUB", 0)
                    result_text += f"• **{source}:** ₽{price:,}\n"
            
            # Quest usage
            if item_data.get("usedInTasks"):
                result_text += f"\n## Used in Quests\n"
                for task in item_data["usedInTasks"]:
                    trader = task.get("trader", {}).get("name", "Unknown")
                    result_text += f"• **{task['name']}** (from {trader})\n"
            
            # Links
            if item.wiki_link:
                result_text += f"\n**Wiki:** {item.wiki_link}\n"
            
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
                    items_data = await client.search_items(name=item_name, limit=1)
                    if items_data:
                        item = parse_item_from_api(items_data[0])
                        all_prices.append(item)
                    else:
                        # Create a minimal item for error case
                        error_item = Item(id="", name=item_name)
                        error_item.error = "Not found"  # Add error attribute
                        all_prices.append(error_item)
            
            result_text = f"# Item Prices ({len(item_names)} requested)\n\n"
            
            for item in all_prices:
                if hasattr(item, 'error'):
                    result_text += f"• **{item.name}**: {item.error}\n"
                else:
                    result_text += f"• **{item.name}**\n"
                    if item.avg24h_price and item.avg24h_price > 0:
                        result_text += f"  - Average: ₽{item.avg24h_price:,}\n"
                        if item.low24h_price and item.high24h_price:
                            result_text += f"  - Range: ₽{item.low24h_price:,} - ₽{item.high24h_price:,}\n"
                        if item.change_last48h_percent and item.change_last48h_percent != 0:
                            trend = "📈" if item.change_last48h_percent > 0 else "📉"
                            result_text += f"  - 48h Change: {item.change_last48h_percent:+.1f}% {trend}\n"
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
                    item_data = await client.get_item_by_id(item_id)
                    if item_data:
                        item = parse_item_from_api(item_data)
                        # Store raw data for fields not in schema
                        item._raw_data = item_data
                        items.append(item)
                    else:
                        error_item = Item(id=item_id, name="")
                        error_item.error = "Not found"
                        items.append(error_item)
            
            result_text = f"# Item Comparison ({len(items)} items)\n\n"
            
            # Basic info comparison
            result_text += "## Basic Information\n"
            result_text += "| Item | Weight | Size | Base Price |\n"
            result_text += "|------|--------|------|------------|\n"
            
            for item in items:
                if hasattr(item, 'error'):
                    result_text += f"| {item.id} | Error: {item.error} | - | - |\n"
                else:
                    weight = item.weight or 0
                    width = getattr(item, '_raw_data', {}).get('width', 0)
                    height = getattr(item, '_raw_data', {}).get('height', 0)
                    base_price = item.base_price or 0
                    
                    result_text += f"| {item.name} | {weight}kg | {width}x{height} | ₽{base_price:,} |\n"
            
            # Market prices comparison
            result_text += "\n## Market Prices\n"
            result_text += "| Item | 24h Average | 24h Low | 24h High | 48h Change |\n"
            result_text += "|------|-------------|---------|----------|------------|\n"
            
            for item in items:
                if not hasattr(item, 'error'):
                    avg_price = item.avg24h_price or 0
                    low_price = item.low24h_price or 0
                    high_price = item.high24h_price or 0
                    change_48h = item.change_last48h_percent or 0
                    
                    avg_text = f"₽{avg_price:,}" if avg_price > 0 else "N/A"
                    low_text = f"₽{low_price:,}" if low_price > 0 else "N/A"
                    high_text = f"₽{high_price:,}" if high_price > 0 else "N/A"
                    change_text = f"{change_48h:+.1f}%" if change_48h != 0 else "0%"
                    
                    result_text += f"| {item.name} | {avg_text} | {low_text} | {high_text} | {change_text} |\n"
            
            # Value analysis
            valid_items = [item for item in items if not hasattr(item, 'error') and (item.avg24h_price or 0) > 0]
            if len(valid_items) > 1:
                result_text += "\n## Value Analysis\n"
                
                # Price per slot
                result_text += "### Price per Inventory Slot\n"
                for item in valid_items:
                    avg_price = item.avg24h_price or 0
                    width = getattr(item, '_raw_data', {}).get('width', 1)
                    height = getattr(item, '_raw_data', {}).get('height', 1)
                    slots = width * height
                    price_per_slot = avg_price / slots if slots > 0 else 0
                    
                    result_text += f"• **{item.name}**: ₽{price_per_slot:,.0f} per slot\n"
                
                # Best value
                def get_value_ratio(item):
                    avg_price = item.avg24h_price or 0
                    width = getattr(item, '_raw_data', {}).get('width', 1)
                    height = getattr(item, '_raw_data', {}).get('height', 1)
                    return avg_price / (width * height)
                
                best_value_item = max(valid_items, key=get_value_ratio)
                result_text += f"\n**Best Value:** {best_value_item.name}\n"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"Error comparing items: {e}")
            return [TextContent(
                type="text",
                text=f"Error comparing items: {str(e)}"
            )]
