# Tarkov MCP Server

A Model Context Protocol (MCP) server that provides access to Escape from Tarkov game data through the community-maintained Tarkov API.

## Features

### High Priority Tools (Implemented)

- **search_items** - Search for items by name or type
- **get_item_details** - Get detailed item information including prices, stats, and usage
- **get_flea_market_data** - Current flea market price data
- **get_barter_trades** - Available barter exchanges from traders
- **calculate_barter_profit** - Profit/loss analysis for barter trades

## Installation

```bash
pip install -r requirements.txt
```

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Running the Server

```bash
python -m src.server
```

## Configuration

The server can be configured using environment variables:

- `TARKOV_API_URL` - Tarkov API endpoint (default: https://api.tarkov.dev/graphql)
- `MAX_REQUESTS_PER_MINUTE` - Rate limit (default: 60)
- `REQUEST_TIMEOUT` - Request timeout in seconds (default: 30)

## Usage Examples

### Search for Items

```json
{
  "name": "search_items",
  "arguments": {
    "name": "AK",
    "limit": 10
  }
}
```

### Get Item Details

```json
{
  "name": "get_item_details",
  "arguments": {
    "item_id": "5ac66d015acfc4001633997a"
  }
}
```

### Get Flea Market Data

```json
{
  "name": "get_flea_market_data",
  "arguments": {
    "limit": 50
  }
}
```

### Calculate Barter Profit

```json
{
  "name": "calculate_barter_profit",
  "arguments": {
    "barter_id": "5ac66d015acfc4001633997a"
  }
}
```

## API Data Source

This server uses the community-maintained Tarkov API at https://api.tarkov.dev/graphql, which provides real-time data for Escape from Tarkov including:

- Item information and statistics
- Current market prices
- Trader information and barter trades
- Quest and task data
- Map and location information

## License

GPL-3.0 License - see LICENSE file for details.
