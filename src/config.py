"""Configuration settings for the Tarkov MCP server."""

import os
from typing import Optional

class Config:
    """Configuration class for Tarkov MCP server."""
    
    # Tarkov API settings
    TARKOV_API_URL: str = "https://api.tarkov.dev/graphql"
    
    # Rate limiting
    MAX_REQUESTS_PER_MINUTE: int = 60
    REQUEST_TIMEOUT: int = 30
    
    # Caching
    CACHE_TTL_ITEMS: int = 3600  # 1 hour for items
    CACHE_TTL_PRICES: int = 300  # 5 minutes for prices
    
    # User agent
    USER_AGENT: str = "TarkovMCPServer/0.1.0"
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables."""
        config = cls()
        
        # Override with environment variables if present
        if url := os.getenv("TARKOV_API_URL"):
            config.TARKOV_API_URL = url
            
        if rate_limit := os.getenv("MAX_REQUESTS_PER_MINUTE"):
            config.MAX_REQUESTS_PER_MINUTE = int(rate_limit)
            
        if timeout := os.getenv("REQUEST_TIMEOUT"):
            config.REQUEST_TIMEOUT = int(timeout)
            
        return config

# Global config instance
config = Config.from_env()