"""Map-related MCP tools."""

from typing import List, Dict, Any
from mcp.types import Tool, TextContent
import logging

from tarkov_mcp.graphql_client import TarkovGraphQLClient
from tarkov_mcp.schema import Map, parse_map_from_api

logger = logging.getLogger(__name__)

class MapTools:
    """Map-related tools for the MCP server."""
    
    def __init__(self):
        self.tools = [
            Tool(
                name="get_maps",
                description="Get information about all available maps",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="get_map_details",
                description="Get detailed information about a specific map",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "map_name": {
                            "type": "string",
                            "description": "Name of the map to get details for"
                        }
                    },
                    "required": ["map_name"]
                }
            ),
            Tool(
                name="get_map_spawns",
                description="Get spawn locations and boss information for a map",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "map_name": {
                            "type": "string",
                            "description": "Name of the map to get spawn information for"
                        }
                    },
                    "required": ["map_name"]
                }
            )
        ]
    
    async def handle_get_maps(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get_maps tool call."""
        try:
            async with TarkovGraphQLClient() as client:
                maps_data = await client.get_maps()
            
            if not maps_data:
                return [TextContent(
                    type="text",
                    text="No maps found"
                )]
            
            # Parse maps using schema
            maps = [parse_map_from_api(map_data) for map_data in maps_data]
            
            result_text = f"# Available Maps ({len(maps)} found)\n\n"
            
            for map_obj in maps:
                result_text += f"## {map_obj.name}\n"
                if map_obj.description:
                    result_text += f"**Description:** {map_obj.description}\n"
                if map_obj.raidDuration and map_obj.raidDuration > 0:
                    result_text += f"**Raid Duration:** {map_obj.raidDuration} minutes\n"
                if map_obj.players and map_obj.players != "Unknown":
                    result_text += f"**Players:** {map_obj.players}\n"
                
                # Boss information
                if map_obj.bosses:
                    boss_names = []
                    for boss in map_obj.bosses:
                        if isinstance(boss, dict):
                            boss_names.append(boss.get('boss', {}).get('name', 'Unknown'))
                        else:
                            boss_names.append(getattr(boss, 'name', 'Unknown'))
                    result_text += f"**Bosses:** {', '.join(boss_names)}\n"
                
                result_text += "\n"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"Error getting maps: {e}")
            return [TextContent(
                type="text",
                text=f"Error getting maps: {str(e)}"
            )]
    
    async def handle_get_map_details(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get_map_details tool call."""
        map_name = arguments.get("map_name")
        
        if not map_name:
            return [TextContent(
                type="text",
                text="Error: 'map_name' is required"
            )]
        
        try:
            async with TarkovGraphQLClient() as client:
                map_data = await client.get_map_by_name(map_name)
            
            if not map_data:
                return [TextContent(
                    type="text",
                    text=f"No map found with name: {map_name}"
                )]
            
            # Parse map using schema
            map_obj = parse_map_from_api(map_data)
            
            result_text = f"# {map_obj.name}\n\n"
            
            if map_obj.description:
                result_text += f"**Description:** {map_obj.description}\n\n"
            
            # Basic info
            result_text += "## Map Information\n"
            if map_obj.raidDuration:
                result_text += f"• **Raid Duration:** {map_obj.raidDuration} minutes\n"
            if map_obj.players:
                result_text += f"• **Players:** {map_obj.players}\n"
            if map_obj.enemies:
                result_text += f"• **Enemies:** {', '.join(map_obj.enemies)}\n"
            
            # Extracts
            if map_data.get("extracts"):
                result_text += f"\n## Extraction Points\n"
                for extract in map_data["extracts"]:
                    extract_name = extract.get("name", "Unknown")
                    result_text += f"• **{extract_name}**\n"
                    if extract.get("faction"):
                        result_text += f"  - Faction: {extract['faction']}\n"
                    if extract.get("switches"):
                        result_text += f"  - Requires switches: {len(extract['switches'])}\n"
            
            # Bosses
            if map_data.get("bosses"):
                result_text += f"\n## Bosses\n"
                for boss in map_data["bosses"]:
                    boss_name = boss.get("name", "Unknown")
                    spawn_chance = boss.get("spawnChance", 0)
                    result_text += f"• **{boss_name}** ({spawn_chance}% spawn chance)\n"
                    
                    if boss.get("spawnLocations"):
                        locations = [loc.get("name", "Unknown") for loc in boss["spawnLocations"]]
                        result_text += f"  - Locations: {', '.join(locations)}\n"
                    
                    if boss.get("escorts"):
                        escort_count = len(boss["escorts"])
                        result_text += f"  - Escorts: {escort_count}\n"
            
            # Loot
            if map_data.get("loot"):
                high_value_loot = [item for item in map_data["loot"] if item.get("item", {}).get("avg24hPrice", 0) > 50000]
                if high_value_loot:
                    result_text += f"\n## High Value Loot (>₽50,000)\n"
                    for loot in high_value_loot[:10]:  # Top 10
                        item = loot.get("item", {})
                        item_name = item.get("name", "Unknown")
                        price = item.get("avg24hPrice", 0)
                        result_text += f"• {item_name}: ₽{price:,}\n"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"Error getting map details: {e}")
            return [TextContent(
                type="text",
                text=f"Error getting map details: {str(e)}"
            )]
    
    async def handle_get_map_spawns(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get_map_spawns tool call."""
        map_name = arguments.get("map_name")
        
        if not map_name:
            return [TextContent(
                type="text",
                text="Error: 'map_name' is required"
            )]
        
        try:
            async with TarkovGraphQLClient() as client:
                map_data = await client.get_map_by_name(map_name)
            
            if not map_data:
                return [TextContent(
                    type="text",
                    text=f"No map found with name: {map_name}"
                )]
            
            result_text = f"# Spawn Information for {map_data['name']}\n\n"
            
            # Boss spawns
            if map_data.get("bosses"):
                result_text += "## Boss Spawns\n"
                for boss in map_data["bosses"]:
                    boss_name = boss.get("name", "Unknown")
                    spawn_chance = boss.get("spawnChance", 0)
                    result_text += f"### {boss_name} ({spawn_chance}% chance)\n"
                    
                    if boss.get("spawnLocations"):
                        for location in boss["spawnLocations"]:
                            loc_name = location.get("name", "Unknown")
                            chance = location.get("chance", 0)
                            result_text += f"• **{loc_name}** - {chance}% chance\n"
                    
                    if boss.get("escorts"):
                        result_text += f"**Escorts:**\n"
                        for escort in boss["escorts"]:
                            escort_name = escort.get("name", "Unknown")
                            escort_count = escort.get("amount", [{}])[0]
                            min_count = escort_count.get("min", 0)
                            max_count = escort_count.get("max", 0)
                            result_text += f"• {escort_name}: {min_count}-{max_count}\n"
                    
                    result_text += "\n"
            else:
                result_text += "No boss spawn information available for this map.\n"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"Error getting map spawns: {e}")
            return [TextContent(
                type="text",
                text=f"Error getting map spawns: {str(e)}"
            )]
