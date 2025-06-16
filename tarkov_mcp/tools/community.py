"""Community and social features MCP tools."""

from typing import List, Dict, Any
from mcp.types import Tool, TextContent
import logging

from tarkov_mcp.graphql_client import TarkovGraphQLClient

logger = logging.getLogger(__name__)

class CommunityTools:
    """Community and social tools for the MCP server."""
    
    def __init__(self):
        self.tools = [
            Tool(
                name="get_goon_reports",
                description="Get recent goon squad sighting reports from the community",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of reports to return",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 50
                        }
                    }
                }
            )
        ]
    
    async def handle_get_goon_reports(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get_goon_reports tool call."""
        limit = arguments.get("limit", 10)
        
        try:
            async with TarkovGraphQLClient() as client:
                goon_reports_data = await client.get_goon_reports(limit=limit)
            
            if not goon_reports_data:
                return [TextContent(
                    type="text",
                    text="No goon squad reports found"
                )]
            
            result_text = f"# Recent Goon Squad Reports ({len(goon_reports_data)} reports)\n\n"
            
            for report in goon_reports_data:
                map_name = report.get('map', {}).get('name', 'Unknown Map')
                timestamp = report.get('timestamp', 'Unknown time')
                location = report.get('location', 'Unknown location')
                spotted_by = report.get('spottedBy', 'Anonymous')
                verified = report.get('verified', False)
                
                status_emoji = "✅" if verified else "⚠️"
                verification_status = "Verified" if verified else "Unverified"
                
                result_text += f"## {status_emoji} {map_name} - {location}\n"
                result_text += f"**Time:** {timestamp}\n"
                result_text += f"**Reported by:** {spotted_by}\n"
                result_text += f"**Status:** {verification_status}\n\n"
                result_text += "---\n\n"
            
            result_text += "\n💡 **Note:** Goon squads are roaming boss groups that can appear on various maps. "
            result_text += "These reports are community-driven and may not be 100% accurate. Always be cautious when entering areas with recent sightings.\n"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"Error getting goon reports: {e}")
            return [TextContent(
                type="text",
                text=f"Error getting goon reports: {str(e)}"
            )]