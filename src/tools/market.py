"""Market and trading related MCP tools."""

from typing import List, Dict, Any
from mcp.types import Tool, TextContent
import logging

from graphql_client import TarkovGraphQLClient

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
            )
        ]
    
    async def handle_get_flea_market_data(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get_flea_market_data tool call."""
        limit = arguments.get("limit", 50)
        
        try:
            async with TarkovGraphQLClient() as client:
                items = await client.get_flea_market_data(limit=limit)
            
            if not items:
                return [TextContent(
                    type="text",
                    text="No flea market data available"
                )]
            
            # Sort by 24h average price (highest first)
            items_with_prices = [item for item in items if item.get("avg24hPrice")]
            items_with_prices.sort(key=lambda x: x.get("avg24hPrice", 0), reverse=True)
            
            result_text = f"# Flea Market Data (Top {len(items_with_prices)} items)\n\n"
            
            for item in items_with_prices[:limit]:
                avg_price = item.get("avg24hPrice", 0)
                low_price = item.get("low24hPrice", 0)
                high_price = item.get("high24hPrice", 0)
                change_48h = item.get("changeLast48hPercent", 0)
                
                result_text += f"## {item['name']} ({item['shortName']})\n"
                result_text += f"• **Average (24h):** ₽{avg_price:,}\n"
                
                if low_price and high_price:
                    result_text += f"• **Range (24h):** ₽{low_price:,} - ₽{high_price:,}\n"
                
                if change_48h != 0:
                    trend = "📈" if change_48h > 0 else "📉"
                    result_text += f"• **48h Change:** {change_48h:+.1f}% {trend}\n"
                
                result_text += f"• **ID:** {item['id']}\n\n"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"Error getting flea market data: {e}")
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
                    profit = total_value - total_cost
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