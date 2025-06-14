"""Market and trading related MCP tools."""

from typing import List, Dict, Any
from mcp.types import Tool, TextContent
import logging

from tarkov_mcp.graphql_client import TarkovGraphQLClient
from tarkov_mcp.schema import parse_item_from_api

logger = logging.getLogger(__name__)

class MarketTools:
    """Market and trading tools for the MCP server."""
    
    def __init__(self):
        self.tools = [
            Tool(
                name="get_flea_market_data",
                description="Get current flea market price data for items",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of items to return",
                            "default": 50,
                            "minimum": 1,
                            "maximum": 200
                        }
                    }
                }
            ),
            Tool(
                name="get_barter_trades",
                description="Get available barter trades from traders",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of barters to return",
                            "default": 30,
                            "minimum": 1,
                            "maximum": 100
                        }
                    }
                }
            ),
            Tool(
                name="calculate_barter_profit",
                description="Calculate profit/loss for barter trades",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "barter_id": {
                            "type": "string",
                            "description": "ID of the barter trade to analyze"
                        }
                    },
                    "required": ["barter_id"]
                }
            ),
            Tool(
                name="get_ammo_data",
                description="Get ammunition data and statistics",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "caliber": {
                            "type": "string",
                            "description": "Filter by ammunition caliber (e.g., '5.56x45mm', '7.62x39mm')"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of ammo types to return",
                            "default": 50,
                            "minimum": 1,
                            "maximum": 200
                        }
                    }
                }
            ),
            Tool(
                name="get_hideout_modules",
                description="Get hideout modules and their requirements",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="get_crafts",
                description="Get crafting recipes from hideout stations with cost analysis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of crafts to return",
                            "default": 50,
                            "minimum": 1,
                            "maximum": 200
                        },
                        "station": {
                            "type": "string",
                            "description": "Filter by station name (partial match)"
                        }
                    }
                }
            )
        ]
    
    async def handle_get_flea_market_data(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get_flea_market_data tool call."""
        limit = arguments.get("limit", 50)
        
        try:
            async with TarkovGraphQLClient() as client:
                items_data = await client.get_flea_market_data(limit=limit)
            
            if not items_data:
                return [TextContent(
                    type="text",
                    text="No flea market data available"
                )]
            
            # Parse items using schema
            items = [parse_item_from_api(item_data) for item_data in items_data]
            
            # Sort by 24h average price (highest first)
            items_with_prices = [item for item in items if item.avg24h_price]
            items_with_prices.sort(key=lambda x: x.avg24h_price or 0, reverse=True)
            
            result_text = f"# Flea Market Data (Top {len(items_with_prices)} items)\n\n"
            
            for item in items_with_prices[:limit]:
                avg_price = item.avg24h_price or 0
                low_price = item.low24h_price or 0
                high_price = item.high24h_price or 0
                change_48h = item.change_last48h_percent or 0
                
                short_name = item.short_name or ""
                result_text += f"## {item.name} ({short_name})\n"
                result_text += f"• **Average (24h):** ₽{avg_price:,}\n"
                
                if low_price and high_price:
                    result_text += f"• **Range (24h):** ₽{low_price:,} - ₽{high_price:,}\n"
                
                if change_48h != 0:
                    trend = "📈" if change_48h > 0 else "📉"
                    result_text += f"• **48h Change:** {change_48h:+.1f}% {trend}\n"
                
                result_text += f"• **ID:** {item.id}\n\n"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"Error getting flea market data: {e}", exc_info=True)
            return [TextContent(
                type="text",
                text=f"Error getting flea market data: {str(e)}"
            )]
    
    async def handle_get_barter_trades(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get_barter_trades tool call."""
        limit = arguments.get("limit", 30)
        
        try:
            async with TarkovGraphQLClient() as client:
                barters = await client.get_barters(limit=limit)
            
            if not barters:
                return [TextContent(
                    type="text",
                    text="No barter trades available"
                )]
            
            result_text = f"# Available Barter Trades ({len(barters)} found)\n\n"
            
            for barter in barters:
                trader_name = barter.get("trader", {}).get("name", "Unknown")
                level = barter.get("level", 1)
                buy_limit = barter.get("buyLimit")
                
                result_text += f"## Trader: {trader_name} (Level {level})\n"
                result_text += f"**Barter ID:** {barter['id']}\n"
                
                if buy_limit:
                    result_text += f"**Buy Limit:** {buy_limit}\n"
                
                # Required items
                if barter.get("requiredItems"):
                    result_text += f"\n**Required Items:**\n"
                    total_cost = 0
                    for req_item in barter["requiredItems"]:
                        item = req_item.get("item", {})
                        count = req_item.get("count", 1)
                        item_name = item.get("name", "Unknown")
                        avg_price = item.get("avg24hPrice", 0)
                        item_cost = avg_price * count
                        total_cost += item_cost
                        
                        result_text += f"• {count}x {item_name}"
                        if avg_price > 0:
                            result_text += f" (₽{item_cost:,})"
                        result_text += "\n"
                
                # Reward items
                if barter.get("rewardItems"):
                    result_text += f"\n**Reward Items:**\n"
                    total_value = 0
                    for reward_item in barter["rewardItems"]:
                        item = reward_item.get("item", {})
                        count = reward_item.get("count", 1)
                        item_name = item.get("name", "Unknown")
                        avg_price = item.get("avg24hPrice", 0)
                        item_value = avg_price * count
                        total_value += item_value
                        
                        result_text += f"• {count}x {item_name}"
                        if avg_price > 0:
                            result_text += f" (₽{item_value:,})"
                        result_text += "\n"
                
                # Calculate profit if we have price data
                if 'total_cost' in locals() and 'total_value' in locals() and total_cost > 0:
                    profit = total_value - total_cost # type: ignore
                    profit_percent = (profit / total_cost) * 100
                    profit_indicator = "💰" if profit > 0 else "💸"
                    result_text += f"\n**Estimated Profit:** ₽{profit:,} ({profit_percent:+.1f}%) {profit_indicator}\n"
                
                # Task unlock requirement
                if barter.get("taskUnlock"):
                    task = barter["taskUnlock"]
                    result_text += f"\n**Requires Quest:** {task.get('name', 'Unknown')}\n"
                
                result_text += "\n---\n\n"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"Error getting barter trades: {e}")
            return [TextContent(
                type="text",
                text=f"Error getting barter trades: {str(e)}"
            )]
    
    async def handle_calculate_barter_profit(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle calculate_barter_profit tool call."""
        barter_id = arguments.get("barter_id")
        
        if not barter_id:
            return [TextContent(
                type="text",
                text="Error: 'barter_id' is required"
            )]
        
        try:
            async with TarkovGraphQLClient() as client:
                # Get all barters and find the specific one
                barters = await client.get_barters(limit=1000)
                barter = next((b for b in barters if b["id"] == barter_id), None)
            
            if not barter:
                return [TextContent(
                    type="text",
                    text=f"No barter found with ID: {barter_id}"
                )]
            
            trader_name = barter.get("trader", {}).get("name", "Unknown")
            
            result_text = f"# Barter Profit Analysis\n\n"
            result_text += f"**Trader:** {trader_name}\n"
            result_text += f"**Barter ID:** {barter_id}\n\n"
            
            # Calculate required items cost
            total_cost = 0
            result_text += "## Required Items (Cost)\n"
            
            if barter.get("requiredItems"):
                for req_item in barter["requiredItems"]:
                    item = req_item.get("item", {})
                    count = req_item.get("count", 1)
                    item_name = item.get("name", "Unknown")
                    avg_price = item.get("avg24hPrice", 0)
                    item_cost = avg_price * count
                    total_cost += item_cost
                    
                    result_text += f"• {count}x {item_name}: ₽{item_cost:,}\n"
            
            result_text += f"\n**Total Cost:** ₽{total_cost:,}\n\n"
            
            # Calculate reward items value
            total_value = 0
            result_text += "## Reward Items (Value)\n"
            
            if barter.get("rewardItems"):
                for reward_item in barter["rewardItems"]:
                    item = reward_item.get("item", {})
                    count = reward_item.get("count", 1)
                    item_name = item.get("name", "Unknown")
                    avg_price = item.get("avg24hPrice", 0)
                    item_value = avg_price * count
                    total_value += item_value
                    
                    result_text += f"• {count}x {item_name}: ₽{item_value:,}\n"
            
            result_text += f"\n**Total Value:** ₽{total_value:,}\n\n"
            
            # Calculate profit
            if total_cost > 0:
                profit = total_value - total_cost
                profit_percent = (profit / total_cost) * 100
                
                result_text += "## Profit Analysis\n"
                result_text += f"• **Profit/Loss:** ₽{profit:,}\n"
                result_text += f"• **Return on Investment:** {profit_percent:+.1f}%\n"
                
                if profit > 0:
                    result_text += f"• **Status:** 💰 Profitable\n"
                elif profit == 0:
                    result_text += f"• **Status:** ⚖️ Break Even\n"
                else:
                    result_text += f"• **Status:** 💸 Loss\n"
                
                # Additional considerations
                result_text += f"\n## Additional Considerations\n"
                if barter.get("buyLimit"):
                    max_profit = profit * barter["buyLimit"]
                    result_text += f"• **Buy Limit:** {barter['buyLimit']} (Max profit: ₽{max_profit:,})\n"
                
                if barter.get("taskUnlock"):
                    task = barter["taskUnlock"]
                    result_text += f"• **Quest Required:** {task.get('name', 'Unknown')}\n"
                
                trader_level = barter.get("level", 1)
                result_text += f"• **Trader Level Required:** {trader_level}\n"
            else:
                result_text += "## Analysis\n"
                result_text += "⚠️ Cannot calculate profit - missing price data for required items\n"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"Error calculating barter profit: {e}")
            return [TextContent(
                type="text",
                text=f"Error calculating barter profit: {str(e)}"
            )]
    
    async def handle_get_ammo_data(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get_ammo_data tool call."""
        caliber = arguments.get("caliber")
        limit = arguments.get("limit", 50)
        
        try:
            async with TarkovGraphQLClient() as client:
                ammo = await client.get_ammo_data(caliber=caliber, limit=limit)
            
            if not ammo:
                caliber_text = f" for {caliber}" if caliber else ""
                return [TextContent(
                    type="text",
                    text=f"No ammo data found{caliber_text}"
                )]
            
            caliber_text = f" for {caliber}" if caliber else ""
            result_text = f"# Ammo Data{caliber_text}\n\n"
            
            # Group by caliber
            caliber_groups = {}
            for ammo_item in ammo:
                ammo_caliber = ammo_item.get("caliber", "Unknown")
                if ammo_caliber not in caliber_groups:
                    caliber_groups[ammo_caliber] = []
                caliber_groups[ammo_caliber].append(ammo_item)
            
            for cal, ammo_list in caliber_groups.items():
                result_text += f"## {cal}\n"
                
                # Sort by damage
                ammo_list.sort(key=lambda x: x.get("damage", 0), reverse=True)
                
                for ammo_item in ammo_list:
                    name = ammo_item.get("item", {}).get("name", "Unknown")
                    damage = ammo_item.get("damage", 0)
                    penetration = ammo_item.get("penetrationPower", 0)
                    armor_damage = ammo_item.get("armorDamage", 0)
                    price = ammo_item.get("item", {}).get("avg24hPrice", 0)
                    
                    result_text += f"• **{name}**\n"
                    result_text += f"  - Damage: {damage}\n"
                    result_text += f"  - Penetration: {penetration}\n"
                    result_text += f"  - Armor Damage: {armor_damage}%\n"
                    if price > 0:
                        result_text += f"  - Price: ₽{price:,}\n"
                        if damage > 0:
                            damage_per_ruble = damage / price
                            result_text += f"  - Damage/₽: {damage_per_ruble:.3f}\n"
                    result_text += "\n"
                
                result_text += "\n"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"Error getting ammo data: {e}")
            return [TextContent(
                type="text",
                text=f"Error getting ammo data: {str(e)}"
            )]
    
    async def handle_get_hideout_modules(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get_hideout_modules tool call."""
        try:
            async with TarkovGraphQLClient() as client:
                modules = await client.get_hideout_modules()
            
            if not modules:
                return [TextContent(
                    type="text",
                    text="No hideout modules found"
                )]
            
            result_text = f"# Hideout Modules ({len(modules)} found)\n\n"
            
            for module in modules:
                result_text += f"## {module.get('name', 'Unknown')}\n"
                result_text += f"**ID:** {module.get('id', 'N/A')}\n"
                result_text += f"**Normalized Name:** {module.get('normalizedName', 'N/A')}\n"
                
                if module.get('tarkovDataId'):
                    result_text += f"**Tarkov Data ID:** {module['tarkovDataId']}\n"
                
                levels = module.get('levels', [])
                if levels:
                    result_text += f"**Levels:** {len(levels)}\n"
                    for level in levels[:3]:  # Show first 3 levels
                        level_num = level.get('level', 'N/A')
                        construction_time = level.get('constructionTime', 0)
                        result_text += f"- Level {level_num}: {construction_time // 3600}h {(construction_time % 3600) // 60}m"
                        
                        # Show item requirements
                        item_reqs = level.get('itemRequirements', [])
                        if item_reqs:
                            result_text += f" (requires {len(item_reqs)} items)"
                        
                        # Show crafts available
                        crafts = level.get('crafts', [])
                        if crafts:
                            result_text += f" ({len(crafts)} crafts)"
                        
                        result_text += "\n"
                
                if module.get('imageLink'):
                    result_text += f"**Image:** {module['imageLink']}\n"
                
                # Construction requirements
                if module.get("require"):
                    result_text += f"### Construction Requirements\n"
                    for req in module["require"]:
                        if req.get("item"):
                            item_name = req["item"].get("name", "Unknown")
                            count = req.get("count", 1)
                            result_text += f"• {count}x {item_name}\n"
                        elif req.get("module"):
                            module_name = req["module"].get("name", "Unknown")
                            module_level = req.get("level", 1)
                            result_text += f"• {module_name} Level {module_level}\n"
                        elif req.get("skill"):
                            skill_name = req["skill"].get("name", "Unknown")
                            skill_level = req.get("level", 1)
                            result_text += f"• {skill_name} Level {skill_level}\n"
                        elif req.get("trader"):
                            trader_name = req["trader"].get("name", "Unknown")
                            trader_level = req.get("level", 1)
                            result_text += f"• {trader_name} Level {trader_level}\n"
                
                # Bonuses
                if module.get("bonuses"):
                    result_text += f"\n### Bonuses\n"
                    for bonus in module["bonuses"]:
                        bonus_type = bonus.get("type", "Unknown")
                        value = bonus.get("value", 0)
                        result_text += f"• {bonus_type}: {value}\n"
                
                # Crafts
                if module.get("crafts"):
                    result_text += f"\n### Available Crafts\n"
                    for craft in module["crafts"]:
                        craft_duration = craft.get("duration", 0)
                        result_text += f"• Craft (Duration: {craft_duration}s)\n"
                        
                        if craft.get("requiredItems"):
                            result_text += f"  Required:\n"
                            for req_item in craft["requiredItems"]:
                                item_name = req_item.get("item", {}).get("name", "Unknown")
                                count = req_item.get("count", 1)
                                result_text += f"    - {count}x {item_name}\n"
                        
                        if craft.get("rewardItems"):
                            result_text += f"  Produces:\n"
                            for reward_item in craft["rewardItems"]:
                                item_name = reward_item.get("item", {}).get("name", "Unknown")
                                count = reward_item.get("count", 1)
                                result_text += f"    - {count}x {item_name}\n"
                
                result_text += "\n---\n\n"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"Error getting hideout modules: {e}")
            return [TextContent(
                type="text",
                text=f"Error getting hideout modules: {str(e)}"
            )]

    async def handle_get_crafts(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get_crafts tool call."""
        limit = arguments.get("limit", 50)
        station_filter = arguments.get("station")
        
        try:
            async with TarkovGraphQLClient() as client:
                crafts_data = await client.get_crafts(limit=limit)
                
            if not crafts_data:
                return [TextContent(type="text", text="No crafts found.")]
            
            # Filter by station if specified
            if station_filter:
                crafts_data = [
                    craft for craft in crafts_data 
                    if station_filter.lower() in craft.get('station', {}).get('name', '').lower()
                ]
            
            result_text = f"# Crafting Recipes ({len(crafts_data)} found)\n\n"
            
            for craft in crafts_data:
                station = craft.get('station', {})
                station_name = station.get('name', 'Unknown Station')
                level = craft.get('level', 'N/A')
                duration = craft.get('duration', 0)
                
                result_text += f"## {station_name} Level {level}\n"
                result_text += f"**Duration:** {duration // 3600}h {(duration % 3600) // 60}m {duration % 60}s\n"
                
                if craft.get('unlockLevel'):
                    result_text += f"**Unlock Level:** {craft['unlockLevel']}\n"
                
                # Required items
                required_items = craft.get('requiredItems', [])
                if required_items:
                    result_text += "\n**Required Items:**\n"
                    total_cost = 0
                    for req_item in required_items:
                        item = req_item.get('item', {})
                        count = req_item.get('count', 1)
                        item_name = item.get('name', 'Unknown Item')
                        avg_price = item.get('avg24hPrice', 0)
                        if avg_price:
                            item_cost = avg_price * count
                            total_cost += item_cost
                            result_text += f"- {count}x {item_name} (₽{avg_price:,} each = ₽{item_cost:,})\n"
                        else:
                            result_text += f"- {count}x {item_name}\n"
                    
                    if total_cost > 0:
                        result_text += f"**Total Cost:** ₽{total_cost:,}\n"
                
                # Reward items
                reward_items = craft.get('rewardItems', [])
                if reward_items:
                    result_text += "\n**Reward Items:**\n"
                    total_value = 0
                    for reward_item in reward_items:
                        item = reward_item.get('item', {})
                        count = reward_item.get('count', 1)
                        item_name = item.get('name', 'Unknown Item')
                        avg_price = item.get('avg24hPrice', 0)
                        if avg_price:
                            item_value = avg_price * count
                            total_value += item_value
                            result_text += f"- {count}x {item_name} (₽{avg_price:,} each = ₽{item_value:,})\n"
                        else:
                            result_text += f"- {count}x {item_name}\n"
                    
                    if total_value > 0:
                        result_text += f"**Total Value:** ₽{total_value:,}\n"
                        if total_cost > 0:
                            profit = total_value - total_cost
                            profit_margin = (profit / total_cost) * 100 if total_cost > 0 else 0
                            result_text += f"**Profit:** ₽{profit:,} ({profit_margin:+.1f}%)\n"
                
                result_text += "\n"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"Error getting crafts: {e}")
            return [TextContent(type="text", text=f"Error retrieving crafts: {str(e)}")]
