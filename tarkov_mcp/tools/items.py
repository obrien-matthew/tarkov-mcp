"""Item-related MCP tools."""

from typing import List, Dict, Any
from mcp.types import Tool, TextContent
import logging

from tarkov_mcp.graphql_client import TarkovGraphQLClient
from tarkov_mcp.schema import parse_item_from_api

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
                        },
                        "language": {
                            "type": "string",
                            "description": "Language code for localized results (en, ru, de, fr, es, etc.)",
                            "default": "en"
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
            ),
            Tool(
                name="get_quest_items",
                description="Get quest-specific items with their associated tasks",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of quest items to return",
                            "default": 50,
                            "minimum": 1,
                            "maximum": 200
                        },
                        "language": {
                            "type": "string",
                            "description": "Language code for localized results",
                            "default": "en"
                        }
                    }
                }
            )
        ]
    
    async def handle_search_items(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle search_items tool call."""
        name = arguments.get("name")
        item_type = arguments.get("item_type")
        limit = arguments.get("limit", 20)
        language = arguments.get("language", "en")
        
        if not name and not item_type:
            return [TextContent(
                type="text",
                text="Error: Either 'name' or 'item_type' must be provided"
            )]
        
        try:
            async with TarkovGraphQLClient() as client:
                items_data = await client.search_items(name=name, item_type=item_type, limit=limit, lang=language)
            
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
            if item.normalized_name:
                result_text += f"• **Normalized Name:** {item.normalized_name}\n"
            result_text += f"• **Weight:** {item.weight or 'N/A'} kg\n"
            
            # Dimensions
            if item.width and item.height:
                result_text += f"• **Size:** {item.width}x{item.height} slots\n"
            if item.grid_width and item.grid_height:
                result_text += f"• **Grid Size:** {item.grid_width}x{item.grid_height}\n"
            
            # Pricing
            result_text += f"• **Base Price:** ₽{item.base_price or 0:,}\n"
            if item.fleamarket_fee:
                result_text += f"• **Flea Market Fee:** ₽{item.fleamarket_fee:,}\n"
            
            # Categories and types
            if item.category:
                result_text += f"• **Category:** {item.category}\n"
            if item.types:
                result_text += f"• **Types:** {', '.join(item.types)}\n"
            
            # Modifiers
            if item.accuracy_modifier is not None:
                result_text += f"• **Accuracy Modifier:** {item.accuracy_modifier:+.1%}\n"
            if item.recoil_modifier is not None:
                result_text += f"• **Recoil Modifier:** {item.recoil_modifier:+.1%}\n"
            if item.ergonomics_modifier is not None:
                result_text += f"• **Ergonomics Modifier:** {item.ergonomics_modifier:+d}\n"
            
            # Special properties
            if item.has_grid:
                result_text += f"• **Has Internal Grid:** Yes\n"
            if item.blocks_headphones:
                result_text += f"• **Blocks Headphones:** Yes\n"
            
            # Item properties
            if item.properties:
                result_text += "\n## Item Properties\n"
                props = item.properties
                if isinstance(props, dict):
                    if props.get('caliber'):
                        result_text += f"• **Caliber:** {props['caliber']}\n"
                    if props.get('class'):
                        result_text += f"• **Armor Class:** {props['class']}\n"
                    if props.get('durability'):
                        result_text += f"• **Durability:** {props['durability']}\n"
                    if props.get('ergonomics'):
                        result_text += f"• **Ergonomics:** {props['ergonomics']}\n"
                    if props.get('fireRate'):
                        result_text += f"• **Fire Rate:** {props['fireRate']} RPM\n"
                    if props.get('effectiveDistance'):
                        result_text += f"• **Effective Distance:** {props['effectiveDistance']}m\n"
                    if props.get('capacity'):
                        result_text += f"• **Capacity:** {props['capacity']}\n"
                    if props.get('energy'):
                        result_text += f"• **Energy:** {props['energy']:+d}\n"
                    if props.get('hydration'):
                        result_text += f"• **Hydration:** {props['hydration']:+d}\n"
                    if props.get('uses'):
                        result_text += f"• **Uses:** {props['uses']}\n"
                    if props.get('material') and isinstance(props['material'], dict):
                        material = props['material']
                        if material.get('name'):
                            result_text += f"• **Material:** {material['name']}\n"
                        if material.get('destructibility'):
                            result_text += f"• **Destructibility:** {material['destructibility']:.2f}\n"
            
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
            
            # Trading information
            if item.sell_for:
                result_text += "\n## Sell Prices\n"
                for price in item.sell_for[:5]:  # Limit to top 5
                    vendor_name = price.vendor.name if price.vendor else 'Unknown'
                    price_val = price.price_rub
                    currency = price.currency
                    result_text += f"• **{vendor_name}:** ₽{price_val:,} {currency}\n"
            
            if item.buy_for:
                result_text += "\n## Buy Prices\n"
                for price in item.buy_for[:5]:  # Limit to top 5
                    vendor_name = price.vendor.name if price.vendor else 'Unknown'
                    price_val = price.price_rub
                    currency = price.currency
                    result_text += f"• **{vendor_name}:** ₽{price_val:,} {currency}\n"
            
            # Quest usage
            if item.used_in_tasks:
                result_text += f"\n## Used in Quests\n"
                for task in item.used_in_tasks[:5]:  # Limit to 5
                    trader_name = task.trader.name if task.trader else "Unknown"
                    result_text += f"• **{task.name}** (from {trader_name})\n"
            
            # Barter and craft usage
            if item.barters_for:
                result_text += f"\n## Available in Barters ({len(item.barters_for)})\n"
                for barter in item.barters_for[:3]:  # Show first 3
                    trader_name = barter.trader.name if barter.trader else "Unknown"
                    result_text += f"• {trader_name} Level {barter.level}\n"
            
            if item.crafts_for:
                result_text += f"\n## Available in Crafts ({len(item.crafts_for)})\n"
                for craft in item.crafts_for[:3]:  # Show first 3
                    station_name = craft.station.name if craft.station else "Unknown"
                    result_text += f"• {station_name} Level {craft.level}\n"
            
            # Links
            if item.wiki_link:
                result_text += f"\n**Wiki:** {item.wiki_link}\n"
            if item.link:
                result_text += f"**Tarkov.dev:** {item.link}\n"
            
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
            
            result_text = f"# Item Prices ({len(item_names)} requested)\n\n"
            
            for item in all_prices:
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
                        items.append(item)
            
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
                    width = item.width or 0
                    height = item.height or 0
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
                    width = item.width or 1
                    height = item.height or 1
                    slots = width * height
                    price_per_slot = avg_price / slots if slots > 0 else 0
                    
                    result_text += f"• **{item.name}**: ₽{price_per_slot:,.0f} per slot\n"
                
                # Best value
                def get_value_ratio(item):
                    avg_price = item.avg24h_price or 0
                    width = item.width or 1
                    height = item.height or 1
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

    async def handle_get_quest_items(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get_quest_items tool call."""
        limit = arguments.get("limit", 50)
        language = arguments.get("language", "en")
        
        try:
            async with TarkovGraphQLClient() as client:
                quest_items_data = await client.get_quest_items(limit=limit, lang=language)
            
            if not quest_items_data:
                return [TextContent(
                    type="text",
                    text="No quest items found"
                )]
            
            result_text = f"# Quest Items ({len(quest_items_data)} found)\n\n"
            
            for item in quest_items_data:
                result_text += f"## {item.get('name', 'Unknown Item')}\n"
                
                if item.get('shortName'):
                    result_text += f"**Short Name:** {item['shortName']}\n"
                
                if item.get('description'):
                    result_text += f"**Description:** {item['description']}\n"
                
                # Size and price info
                width = item.get('width', 1)
                height = item.get('height', 1)
                base_price = item.get('basePrice', 0)
                result_text += f"**Size:** {width}x{height} slots\n"
                result_text += f"**Base Price:** ₽{base_price:,}\n"
                
                # Quest usage
                used_in = item.get('usedInTasks', [])
                received_from = item.get('receivedFromTasks', [])
                
                if used_in:
                    result_text += f"\n**Used in Quests ({len(used_in)}):**\n"
                    for task in used_in[:5]:  # Limit to 5
                        trader_name = task.get('trader', {}).get('name', 'Unknown')
                        min_level = task.get('minPlayerLevel', 'N/A')
                        exp = task.get('experience', 0)
                        result_text += f"• {task['name']} ({trader_name}, Lv.{min_level}, {exp} XP)\n"
                    
                    if len(used_in) > 5:
                        result_text += f"• ... and {len(used_in) - 5} more\n"
                
                if received_from:
                    result_text += f"\n**Received from Quests ({len(received_from)}):**\n"
                    for task in received_from[:3]:  # Limit to 3
                        trader_name = task.get('trader', {}).get('name', 'Unknown')
                        result_text += f"• {task['name']} ({trader_name})\n"
                    
                    if len(received_from) > 3:
                        result_text += f"• ... and {len(received_from) - 3} more\n"
                
                # Links
                if item.get('wikiLink'):
                    result_text += f"\n**Wiki:** {item['wikiLink']}\n"
                
                result_text += "\n---\n\n"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"Error getting quest items: {e}")
            return [TextContent(
                type="text",
                text=f"Error getting quest items: {str(e)}"
            )]
