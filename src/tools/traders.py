"""Trader-related MCP tools."""

from typing import List, Dict, Any
from mcp.types import Tool, TextContent
import logging

from graphql_client import TarkovGraphQLClient

logger = logging.getLogger(__name__)

class TraderTools:
    """Trader-related tools for the MCP server."""
    
    def __init__(self):
        self.tools = [
            Tool(
                name="get_traders",
                description="Get information about all traders",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="get_trader_details",
                description="Get detailed information about a specific trader",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "trader_name": {
                            "type": "string",
                            "description": "Name of the trader to get details for"
                        }
                    },
                    "required": ["trader_name"]
                }
            ),
            Tool(
                name="get_trader_items",
                description="Get items sold by a specific trader",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "trader_name": {
                            "type": "string",
                            "description": "Name of the trader"
                        },
                        "level": {
                            "type": "integer",
                            "description": "Trader level (1-4)",
                            "minimum": 1,
                            "maximum": 4
                        }
                    },
                    "required": ["trader_name"]
                }
            )
        ]
    
    async def handle_get_traders(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get_traders tool call."""
        try:
            async with TarkovGraphQLClient() as client:
                traders = await client.get_traders()
            
            if not traders:
                return [TextContent(
                    type="text",
                    text="No traders found"
                )]
            
            result_text = f"# Available Traders ({len(traders)} found)\n\n"
            
            for trader in traders:
                name = trader.get("name", "Unknown")
                description = trader.get("description", "")
                location = trader.get("location", "")
                
                result_text += f"## {name}\n"
                if description:
                    result_text += f"**Description:** {description}\n"
                if location:
                    result_text += f"**Location:** {location}\n"
                
                # Reset times
                if trader.get("resetTime"):
                    result_text += f"**Reset Time:** {trader['resetTime']} hours\n"
                
                # Currency
                if trader.get("currency"):
                    currencies = [curr.get("name", "Unknown") for curr in trader["currency"]]
                    result_text += f"**Accepts:** {', '.join(currencies)}\n"
                
                result_text += "\n"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"Error getting traders: {e}")
            return [TextContent(
                type="text",
                text=f"Error getting traders: {str(e)}"
            )]
    
    async def handle_get_trader_details(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get_trader_details tool call."""
        trader_name = arguments.get("trader_name")
        
        if not trader_name:
            return [TextContent(
                type="text",
                text="Error: 'trader_name' is required"
            )]
        
        try:
            async with TarkovGraphQLClient() as client:
                trader = await client.get_trader_by_name(trader_name)
            
            if not trader:
                return [TextContent(
                    type="text",
                    text=f"No trader found with name: {trader_name}"
                )]
            
            result_text = f"# {trader['name']}\n\n"
            
            if trader.get("description"):
                result_text += f"**Description:** {trader['description']}\n\n"
            
            # Basic info
            result_text += "## Trader Information\n"
            if trader.get("location"):
                result_text += f"• **Location:** {trader['location']}\n"
            if trader.get("resetTime"):
                result_text += f"• **Reset Time:** {trader['resetTime']} hours\n"
            
            # Currency accepted
            if trader.get("currency"):
                currencies = [curr.get("name", "Unknown") for curr in trader["currency"]]
                result_text += f"• **Accepts:** {', '.join(currencies)}\n"
            
            # Levels and requirements
            if trader.get("levels"):
                result_text += f"\n## Loyalty Levels\n"
                for level in trader["levels"]:
                    level_num = level.get("level", 0)
                    result_text += f"### Level {level_num}\n"
                    
                    if level.get("requiredPlayerLevel"):
                        result_text += f"• **Required Player Level:** {level['requiredPlayerLevel']}\n"
                    if level.get("requiredReputation"):
                        result_text += f"• **Required Reputation:** {level['requiredReputation']}\n"
                    if level.get("requiredCommerce"):
                        result_text += f"• **Required Commerce:** ₽{level['requiredCommerce']:,}\n"
                    
                    # Paywall
                    if level.get("paywall"):
                        paywall = level["paywall"]
                        if paywall.get("level") and paywall.get("level") > 0:
                            result_text += f"• **Paywall:** Level {paywall['level']}\n"
                    
                    result_text += "\n"
            
            # Insurance
            if trader.get("insurance"):
                insurance = trader["insurance"]
                result_text += f"## Insurance\n"
                result_text += f"• **Available:** {'Yes' if insurance.get('availableOnMap') else 'No'}\n"
                if insurance.get("minReturnHour"):
                    result_text += f"• **Min Return Time:** {insurance['minReturnHour']} hours\n"
                if insurance.get("maxReturnHour"):
                    result_text += f"• **Max Return Time:** {insurance['maxReturnHour']} hours\n"
                if insurance.get("maxStorageTime"):
                    result_text += f"• **Storage Time:** {insurance['maxStorageTime']} hours\n"
            
            # Repair services
            if trader.get("repair"):
                repair = trader["repair"]
                result_text += f"\n## Repair Services\n"
                result_text += f"• **Available:** {'Yes' if repair.get('availability') else 'No'}\n"
                if repair.get("priceModifier"):
                    result_text += f"• **Price Modifier:** {repair['priceModifier']:.2f}x\n"
                if repair.get("qualityModifier"):
                    result_text += f"• **Quality Modifier:** {repair['qualityModifier']:.2f}x\n"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"Error getting trader details: {e}")
            return [TextContent(
                type="text",
                text=f"Error getting trader details: {str(e)}"
            )]
    
    async def handle_get_trader_items(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get_trader_items tool call."""
        trader_name = arguments.get("trader_name")
        level = arguments.get("level")
        
        if not trader_name:
            return [TextContent(
                type="text",
                text="Error: 'trader_name' is required"
            )]
        
        try:
            async with TarkovGraphQLClient() as client:
                items = await client.get_trader_items(trader_name, level)
            
            if not items:
                level_text = f" at level {level}" if level else ""
                return [TextContent(
                    type="text",
                    text=f"No items found for trader {trader_name}{level_text}"
                )]
            
            level_text = f" (Level {level})" if level else ""
            result_text = f"# {trader_name} Items{level_text}\n\n"
            result_text += f"Found {len(items)} items:\n\n"
            
            # Group items by category if available
            categorized_items = {}
            for item in items:
                categories = item.get("item", {}).get("types", ["Other"])
                category = categories[0] if categories else "Other"
                if category not in categorized_items:
                    categorized_items[category] = []
                categorized_items[category].append(item)
            
            for category, category_items in categorized_items.items():
                result_text += f"## {category}\n"
                
                for trader_item in category_items:
                    item = trader_item.get("item", {})
                    item_name = item.get("name", "Unknown")
                    price = trader_item.get("priceRUB", 0)
                    currency = trader_item.get("currency", "RUB")
                    min_level = trader_item.get("minTraderLevel", 1)
                    
                    result_text += f"• **{item_name}**\n"
                    result_text += f"  - Price: {price:,} {currency}\n"
                    result_text += f"  - Min Level: {min_level}\n"
                    
                    # Stock and restock info
                    if trader_item.get("buyLimit"):
                        result_text += f"  - Buy Limit: {trader_item['buyLimit']}\n"
                    if trader_item.get("restockAmount"):
                        result_text += f"  - Restock: {trader_item['restockAmount']}\n"
                    
                    # Requirements
                    if trader_item.get("requirements"):
                        req_text = []
                        for req in trader_item["requirements"]:
                            req_type = req.get("type", "unknown")
                            req_value = req.get("value", 0)
                            if req_type == "playerLevel":
                                req_text.append(f"Player Level {req_value}")
                            elif req_type == "loyaltyLevel":
                                req_text.append(f"Loyalty Level {req_value}")
                            elif req_type == "questCompleted":
                                req_text.append(f"Quest: {req.get('stringValue', 'Unknown')}")
                        
                        if req_text:
                            result_text += f"  - Requirements: {', '.join(req_text)}\n"
                    
                    result_text += "\n"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"Error getting trader items: {e}")
            return [TextContent(
                type="text",
                text=f"Error getting trader items: {str(e)}"
            )]
