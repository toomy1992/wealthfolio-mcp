# Wealthfolio MCP Server

A Model Context Protocol (MCP) server that integrates with Wealthfolio to provide portfolio data, valuations, and analytics to OpenWebUI and other MCP-compatible applications.

## Features

- **Real-time Portfolio Data**: Fetch current portfolio valuations, holdings, and performance metrics
- **Account Management**: Access all your Wealthfolio accounts and their details
- **Asset Information**: Get comprehensive asset profiles and market data
- **Historical Valuations**: Retrieve portfolio performance history over time
- **OpenWebUI Integration**: Seamlessly integrate with OpenWebUI for enhanced AI interactions
- **n8n Workflow Support**: Ready for automation workflows with n8n

## Prerequisites

- Python 3.10+
- Wealthfolio API access
- OpenWebUI (for UI integration)
- n8n (optional, for workflow automation)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/toomy1992/Wealthfolio-MCP.git
   cd Wealthfolio-MCP
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Wealthfolio API key
   ```

4. **Update your API key in `.env`:**
   ```env
   API_KEY=your_wealthfolio_api_key_here
   API_BASE_URL=https://wealthfolio.labruntipi.io/api/v1
   ```

## Usage

### Starting the Server

```bash
uvicorn src.mcp_server:app --reload
```

The server will start on `http://127.0.0.1:8000`

### API Endpoints

- `GET /portfolio` - Get comprehensive portfolio data including accounts, valuations, assets, and historical performance
- `POST /sync` - Trigger portfolio synchronization (placeholder for future implementation)

### Testing the API

Visit `http://127.0.0.1:8000/docs` for interactive API documentation.

Or test with curl:
```bash
curl -X GET "http://127.0.0.1:8000/portfolio" -H "accept: application/json"
```

## OpenWebUI Integration

1. **Install the MCP plugin** in OpenWebUI
2. **Configure the MCP server URL:** `http://127.0.0.1:8000`
3. **Add tools for portfolio queries:**
   - Portfolio summary
   - Account valuations
   - Asset performance
   - Historical charts

### Example OpenWebUI Queries

- "What's my current portfolio value?"
- "Show me my account performance over the last month"
- "Which assets have the highest gains?"
- "Display my portfolio allocation by asset type"

## n8n Integration

Create automated workflows in n8n:

1. **HTTP Request Node**: Connect to `http://127.0.0.1:8000/portfolio`
2. **Schedule Trigger**: Set up daily/weekly portfolio reports
3. **Data Processing**: Transform portfolio data for notifications
4. **Email/Discord Integration**: Send automated portfolio updates

### Sample n8n Workflow

```
Schedule Trigger → HTTP Request (Portfolio) → Data Transform → Email Notification
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEY` | Your Wealthfolio API key | Required |
| `API_BASE_URL` | Wealthfolio API base URL | `https://wealthfolio.labruntipi.io/api/v1` |
| `asset_filters` | Asset types to filter | `["stocks", "crypto"]` |

### API Endpoints Used

The server integrates with these Wealthfolio API endpoints:

- `/api/v1/accounts` - Account information
- `/api/v1/valuations/latest` - Current portfolio valuations
- `/api/v1/assets` - Asset profiles and data
- `/api/v1/valuations/history` - Historical performance data
- `/api/v1/holdings/item` - Individual holding details

## Development

### Project Structure

```
wealthfolio-mcp/
├── src/
│   ├── mcp_server.py      # FastAPI MCP server
│   └── api_client.py       # Wealthfolio API client
├── config/
│   └── settings.py         # Configuration management
├── tests/                  # Unit and integration tests
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
└── README.md              # This file
```

### Running Tests

```bash
pytest tests/
```

### Adding New Features

1. Extend the `WealthfolioClient` class in `api_client.py`
2. Add new endpoints in `mcp_server.py`
3. Update the README with new functionality

## Troubleshooting

### Common Issues

1. **API Key Invalid**: Verify your API key in `.env`
2. **Connection Errors**: Check internet connectivity and API URL
3. **Empty Responses**: Ensure your Wealthfolio instance has data
4. **CORS Issues**: Configure OpenWebUI CORS settings for the MCP server

### Debug Mode

Run with debug logging:
```bash
uvicorn src.mcp_server:app --reload --log-level debug
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/toomy1992/Wealthfolio-MCP/issues)
- **Discussions**: [GitHub Discussions](https://github.com/toomy1992/Wealthfolio-MCP/discussions)
- **Wealthfolio Community**: [Discord](https://discord.gg/WDMCY6aPWK)

## Changelog

### v0.1.0
- Initial release
- Basic portfolio data integration
- OpenWebUI compatibility
- n8n workflow support
