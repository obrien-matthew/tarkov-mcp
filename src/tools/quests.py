"""Quest-related MCP tools."""

from typing import List, Dict, Any
from mcp.types import Tool, TextContent
import logging

from graphql_client import TarkovGraphQLClient

logger = logging.getLogger(__name__)

class QuestTools:
    """Quest-related tools for the MCP server."""
    
    def __init__(self):
        self.tools = [
            Tool(
                name="get_quests",
                description="Get information about all quests/tasks",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "trader": {
                            "type": "string",
                            "description": "Filter quests by trader name"
                        }
                    }
                }
            ),
            Tool(
                name="get_quest_details",
                description="Get detailed information about a specific quest",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "quest_id": {
                            "type": "string",
                            "description": "ID of the quest to get details for"
                        }
                    },
                    "required": ["quest_id"]
                }
            ),
            Tool(
                name="search_quests",
                description="Search for quests by name or description",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search term for quest name or description"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 20,
                            "minimum": 1,
                            "maximum": 100
                        }
                    },
                    "required": ["query"]
                }
            )
        ]
    
    async def handle_get_quests(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get_quests tool call."""
        trader = arguments.get("trader")
        
        try:
            async with TarkovGraphQLClient() as client:
                quests = await client.get_quests(trader=trader)
            
            if not quests:
                trader_text = f" from {trader}" if trader else ""
                return [TextContent(
                    type="text",
                    text=f"No quests found{trader_text}"
                )]
            
            trader_text = f" from {trader}" if trader else ""
            result_text = f"# Available Quests{trader_text} ({len(quests)} found)\n\n"
            
            # Group by trader
            trader_quests = {}
            for quest in quests:
                trader_name = quest.get("trader", {}).get("name", "Unknown")
                if trader_name not in trader_quests:
                    trader_quests[trader_name] = []
                trader_quests[trader_name].append(quest)
            
            for trader_name, quest_list in trader_quests.items():
                result_text += f"## {trader_name} ({len(quest_list)} quests)\n"
                
                for quest in quest_list:
                    quest_name = quest.get("name", "Unknown")
                    min_level = quest.get("minPlayerLevel", 0)
                    
                    result_text += f"• **{quest_name}**"
                    if min_level > 0:
                        result_text += f" (Level {min_level}+)"
                    result_text += f"\n"
                    result_text += f"  ID: {quest.get('id', 'Unknown')}\n"
                    
                    # Experience reward
                    if quest.get("experience"):
                        result_text += f"  XP: {quest['experience']:,}\n"
                    
                    # Prerequisites
                    if quest.get("taskRequirements"):
                        prereq_count = len(quest["taskRequirements"])
                        result_text += f"  Prerequisites: {prereq_count} quest(s)\n"
                    
                    result_text += "\n"
                
                result_text += "\n"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"Error getting quests: {e}")
            return [TextContent(
                type="text",
                text=f"Error getting quests: {str(e)}"
            )]
    
    async def handle_get_quest_details(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get_quest_details tool call."""
        quest_id = arguments.get("quest_id")
        
        if not quest_id:
            return [TextContent(
                type="text",
                text="Error: 'quest_id' is required"
            )]
        
        try:
            async with TarkovGraphQLClient() as client:
                quest = await client.get_quest_by_id(quest_id)
            
            if not quest:
                return [TextContent(
                    type="text",
                    text=f"No quest found with ID: {quest_id}"
                )]
            
            result_text = f"# {quest['name']}\n\n"
            
            # Basic info
            trader_name = quest.get("trader", {}).get("name", "Unknown")
            result_text += f"**Trader:** {trader_name}\n"
            result_text += f"**ID:** {quest['id']}\n"
            
            if quest.get("minPlayerLevel"):
                result_text += f"**Minimum Level:** {quest['minPlayerLevel']}\n"
            
            if quest.get("experience"):
                result_text += f"**Experience Reward:** {quest['experience']:,} XP\n"
            
            result_text += "\n"
            
            # Description
            if quest.get("description"):
                result_text += f"## Description\n{quest['description']}\n\n"
            
            # Prerequisites
            if quest.get("taskRequirements"):
                result_text += f"## Prerequisites\n"
                for req in quest["taskRequirements"]:
                    req_quest = req.get("task", {})
                    req_name = req_quest.get("name", "Unknown")
                    result_text += f"• Complete: **{req_name}**\n"
                result_text += "\n"
            
            # Objectives
            if quest.get("objectives"):
                result_text += f"## Objectives\n"
                for i, objective in enumerate(quest["objectives"], 1):
                    obj_description = objective.get("description", "Unknown objective")
                    result_text += f"{i}. {obj_description}\n"
                    
                    # Optional objective details
                    if objective.get("optional"):
                        result_text += "   *(Optional)*\n"
                    
                    # Target details
                    if objective.get("target"):
                        targets = objective["target"]
                        if isinstance(targets, list):
                            target_names = [t.get("name", "Unknown") for t in targets]
                            result_text += f"   Targets: {', '.join(target_names)}\n"
                    
                    # Location details
                    if objective.get("maps"):
                        map_names = [m.get("name", "Unknown") for m in objective["maps"]]
                        result_text += f"   Maps: {', '.join(map_names)}\n"
                
                result_text += "\n"
            
            # Rewards
            if quest.get("finishRewards"):
                rewards = quest["finishRewards"]
                result_text += f"## Rewards\n"
                
                # Items
                if rewards.get("items"):
                    result_text += f"### Items\n"
                    for item_reward in rewards["items"]:
                        item = item_reward.get("item", {})
                        count = item_reward.get("count", 1)
                        item_name = item.get("name", "Unknown")
                        result_text += f"• {count}x {item_name}\n"
                
                # Trader reputation
                if rewards.get("traderStanding"):
                    result_text += f"### Trader Reputation\n"
                    for standing in rewards["traderStanding"]:
                        trader_name = standing.get("trader", {}).get("name", "Unknown")
                        standing_value = standing.get("standing", 0)
                        result_text += f"• {trader_name}: {standing_value:+.2f}\n"
                
                # Trader unlocks
                if rewards.get("traderUnlock"):
                    result_text += f"### Trader Unlocks\n"
                    for unlock in rewards["traderUnlock"]:
                        trader_name = unlock.get("name", "Unknown")
                        result_text += f"• Unlocks: {trader_name}\n"
                
                # Skills
                if rewards.get("skillLevelReward"):
                    result_text += f"### Skill Rewards\n"
                    for skill in rewards["skillLevelReward"]:
                        skill_name = skill.get("name", "Unknown")
                        skill_points = skill.get("level", 0)
                        result_text += f"• {skill_name}: +{skill_points} points\n"
                
                result_text += "\n"
            
            # Wiki link
            if quest.get("wikiLink"):
                result_text += f"**Wiki:** {quest['wikiLink']}\n"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"Error getting quest details: {e}")
            return [TextContent(
                type="text",
                text=f"Error getting quest details: {str(e)}"
            )]
    
    async def handle_search_quests(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle search_quests tool call."""
        query = arguments.get("query")
        limit = arguments.get("limit", 20)
        
        if not query:
            return [TextContent(
                type="text",
                text="Error: 'query' is required"
            )]
        
        try:
            async with TarkovGraphQLClient() as client:
                quests = await client.search_quests(query, limit)
            
            if not quests:
                return [TextContent(
                    type="text",
                    text=f"No quests found matching '{query}'"
                )]
            
            result_text = f"# Quest Search Results for '{query}'\n\n"
            result_text += f"Found {len(quests)} matching quests:\n\n"
            
            for quest in quests:
                quest_name = quest.get("name", "Unknown")
                trader_name = quest.get("trader", {}).get("name", "Unknown")
                min_level = quest.get("minPlayerLevel", 0)
                experience = quest.get("experience", 0)
                
                result_text += f"• **{quest_name}** (from {trader_name})\n"
                result_text += f"  ID: {quest.get('id', 'Unknown')}\n"
                
                if min_level > 0:
                    result_text += f"  Min Level: {min_level}\n"
                if experience > 0:
                    result_text += f"  XP Reward: {experience:,}\n"
                
                # Short description if available
                if quest.get("description"):
                    desc = quest["description"][:100]
                    if len(quest["description"]) > 100:
                        desc += "..."
                    result_text += f"  Description: {desc}\n"
                
                result_text += "\n"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"Error searching quests: {e}")
            return [TextContent(
                type="text",
                text=f"Error searching quests: {str(e)}"
            )]
