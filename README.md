# Tarkov MCP Server

A Model Context Protocol (MCP) server that provides access to Escape from Tarkov game data through the community-maintained Tarkov API.

> [!IMPORTANT]  
> I am not affiliated with the tarkov.dev project or API. I simply built this MCP server to interact with what they have built. If you appreciate their work, please consider donating to them [here](https://opencollective.com/tarkov-dev)!

## Features

### Item Tools

- **search_items** - Search for items by name or type (supports localization)
- **get_item_details** - Get detailed item information including prices, stats, and usage
- **get_item_prices** - Get current pricing information for items
- **compare_items** - Compare multiple items side by side
- **get_quest_items** - Get quest-specific items with their associated tasks

### Market Tools

- **get_flea_market_data** - Current flea market price data
- **get_barter_trades** - Available barter exchanges from traders
- **calculate_barter_profit** - Profit/loss analysis for barter trades
- **get_ammo_data** - Ammunition statistics and pricing
- **get_hideout_modules** - Hideout module information and requirements

### Map Tools

- **get_maps** - List all available maps
- **get_map_details** - Detailed map information including spawns and extracts
- **get_map_spawns** - Spawn locations and information for specific maps

### Trader Tools

- **get_traders** - List all traders
- **get_trader_details** - Detailed trader information
- **get_trader_items** - Items available from specific traders

### Quest Tools

- **get_quests** - List quests, optionally filtered by trader
- **get_quest_details** - Detailed quest information including objectives and rewards
- **search_quests** - Search quests by name or description

### Community Tools

- **get_goon_reports** - Get recent community-driven goon squad sighting reports

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install Dependencies

You can install the dependencies in several ways:

First, clone the repository and navigate into the repository root directory.

**Option 1: Install as a package (recommended)**

```bash
pip install -e .
```

**Option 2: Install with development dependencies**

```bash
pip install -e ".[dev]"
```

**Option 3: Using requirements.txt (legacy)**

```bash
pip install -r requirements.txt
```

### Claude Desktop Setup

To use this MCP server with Claude Desktop, make sure you've followed the install instructions above.

Add the following configuration to your Claude Desktop config file:

**On macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**On Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "tarkov": {
      "command": "python",
      "args": ["-m", "tarkov_mcp"],
      "cwd": "/path/to/tarkov-mcp"
    }
  }
}
```

Replace `/path/to/tarkov-mcp` with the actual path to this project directory.

After updating the config file, restart Claude Desktop for the changes to take effect.

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Running the Server

```bash
python -m tarkov_mcp
```

## Configuration

The server can be configured using environment variables:

- `TARKOV_API_URL` - Tarkov API endpoint (default: https://api.tarkov.dev/graphql)
- `MAX_REQUESTS_PER_MINUTE` - Rate limit (default: 60)
- `REQUEST_TIMEOUT` - Request timeout in seconds (default: 30)

## Features

- **Multi-language Support**: Full localization support for 16 languages (English, Russian, German, French, Spanish, etc.)
- **Enhanced Item Data**: Comprehensive item properties including new weapon ballistics, armor materials, and medical effects
- **Community Integration**: Goon squad tracking and quest-specific item information
- **Modern API Compatibility**: Updated GraphQL queries using latest Tarkov API schema structure
- **Rate Limiting**: Built-in rate limiting to respect API limits (60 requests per minute by default)
- **Error Handling**: Comprehensive error handling with detailed error messages
- **Async Support**: Fully asynchronous implementation for better performance
- **Comprehensive Testing**: Extensive test suite with pytest
- **Type Safety**: Full type hints throughout the codebase

## API Data Source

This server uses the community-maintained Tarkov API at https://api.tarkov.dev/graphql, which provides real-time data for Escape from Tarkov including:

- Item information and statistics
- Current market prices
- Trader information and barter trades
- Quest and task data
- Map and location information
- Ammunition data
- Hideout module requirements

## Troubleshooting

### Common Issues

1. **Rate Limiting**: If you encounter rate limit errors, the server will automatically retry with exponential backoff
2. **Network Issues**: Check your internet connection and ensure the Tarkov API is accessible
3. **Claude Desktop Integration**: Make sure the path in your config file is correct and Python is in your PATH

### Logging

The server includes comprehensive logging. To enable debug logging, set the environment variable:

```bash
export LOG_LEVEL=DEBUG
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

Quick start:

1. Fork the repository
2. Set up development environment: `pip install -e ".[dev]"`
3. Install pre-commit hooks: `pre-commit install`
4. Create a feature branch
5. Make your changes with tests
6. Run quality checks: `pre-commit run --all-files`
7. Submit a pull request

## License

GPL-3.0 License - see LICENSE file for details.
