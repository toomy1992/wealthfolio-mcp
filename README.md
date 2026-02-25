# With Wealthfolio 3.0 build in AI this Repo become obsolete


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

### Option 1: Local Development

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

### Option 2: Docker (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/toomy1992/Wealthfolio-MCP.git
   cd Wealthfolio-MCP
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Wealthfolio API key
   ```

3. **Run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

4. **Or build and run manually:**
   ```bash
   docker build -t wealthfolio-mcp .
   docker run -p 8000:8000 --env-file .env wealthfolio-mcp
   ```

### Option 3: Pre-built Docker Image

Pull the latest release from GitHub Container Registry:

```bash
docker pull ghcr.io/toomy1992/wealthfolio-mcp:latest
docker run -p 8000:8000 --env-file .env ghcr.io/toomy1992/wealthfolio-mcp:latest
```

## Usage

### Starting the Server

```bash
uvicorn src.mcp_server:app --reload
```

The server will start on `http://127.0.0.1:8000`

### API Endpoints

#### Portfolio Data Endpoints

- `GET /portfolio` - Get comprehensive portfolio data including accounts, valuations, assets, and historical performance
  - Uses: `get_accounts()`, `get_latest_valuations()`, `get_assets()`, `get_valuation_history()`, `fetch_portfolio_data()`
  
- `GET /accounts` - Get all accounts
  - Uses: `get_accounts()`
  
- `GET /valuations/latest` - Get latest valuations for specified accounts
  - Query params: `account_ids` (list of account IDs)
  - Uses: `get_latest_valuations()`
  
- `GET /assets` - Get all available assets
  - Uses: `get_assets()`
  
- `GET /valuations/history` - Get historical valuations for a specified account and time period
  - Query params: `account_id` (default: "TOTAL"), `days` (default: 30)
  - Uses: `get_valuation_history()`
  
- `GET /holdings/item` - Get a specific holding item for an account and asset
  - Query params: `account_id`, `asset_id`
  - Uses: `get_holding_item()`

#### System Endpoints

- `POST /sync` - Trigger portfolio synchronization (placeholder for future implementation)

### Testing the API

Visit `http://127.0.0.1:8000/docs` for interactive OpenAPI/Swagger documentation with full schema definitions.

Or test with curl:
```bash
# Get portfolio summary
curl -X GET "http://127.0.0.1:8000/portfolio" -H "accept: application/json"

# Get all accounts
curl -X GET "http://127.0.0.1:8000/accounts" -H "accept: application/json"

# Get assets
curl -X GET "http://127.0.0.1:8000/assets" -H "accept: application/json"

# Get valuation history (last 30 days)
curl -X GET "http://127.0.0.1:8000/valuations/history?account_id=TOTAL&days=30" -H "accept: application/json"

# Get holdings for specific accounts
curl -X GET "http://127.0.0.1:8000/holdings?account_ids=acc1&account_ids=acc2" -H "accept: application/json"
```

This detailed holdings data enables AI agents to perform accurate portfolio rebalancing by calculating exact share quantities, cost basis, and unrealized gains/losses.

## OpenAPI / Swagger Documentation

The server automatically generates comprehensive OpenAPI 3.0 documentation:

- **Interactive Swagger UI**: http://localhost:8000/docs
- **OpenAPI JSON Schema**: http://localhost:8000/openapi.json

All endpoints are documented with:
- Detailed descriptions of what data is fetched
- Information about which WealthfolioClient methods are used
- Parameter documentation and defaults
- Response schemas

## MCP Integration with OpenAPI

This server is designed to work as a universal MCP (Model Context Protocol) server with OpenAPI support:

### Using mcpo Proxy (Recommended)

To expose this MCP server through standard REST/OpenAPI endpoints with the `mcpo` proxy:

```bash
# Install mcpo
pip install mcpo

# Run the MCP server through mcpo proxy
mcpo --host 0.0.0.0 --port 8000 -- uvicorn src.mcp_server:app --host 127.0.0.1 --port 8001
```

This will:
- Convert MCP tools to REST endpoints
- Auto-generate interactive OpenAPI documentation
- Make the server accessible via standard HTTP
- Enable integration with OpenWebUI and other platforms

### Docker with mcpo

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN pip install mcpo uv

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY config/ ./config/

ENV API_KEY=${API_KEY}
ENV API_BASE_URL=${API_BASE_URL}

EXPOSE 8000

CMD ["mcpo", "--host", "0.0.0.0", "--port", "8000", "--", "uvicorn", "src.mcp_server:app", "--host", "127.0.0.1", "--port", "8001"]
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

## CI/CD and Releases

This project uses GitHub Actions for automated building, testing, and releasing.

### Automated Versioning

- Versions start from `0.1.0`
- Patch versions are automatically incremented on each push to `main`
- Releases are created automatically with Docker images

### GitHub Actions Workflow

The CI/CD pipeline includes:
- **Testing**: Runs pytest and linting on all pushes
- **Docker Build**: Builds and pushes Docker images to GitHub Container Registry
- **Automated Releases**: Creates GitHub releases with version tags

### Docker Images

Pre-built images are available at:
```
ghcr.io/toomy1992/wealthfolio-mcp:latest
```

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
├── .github/
│   └── workflows/          # GitHub Actions
├── Dockerfile              # Docker build configuration
├── docker-compose.yml      # Local development setup
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
└── README.md              # This file
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Or use the Makefile
make test
```

### Development Commands

Use the provided Makefile for common development tasks:

```bash
make install      # Install dependencies
make dev          # Run development server
make test         # Run tests
make lint         # Run linting
make format       # Format code
make docker-build # Build Docker image
make docker-run   # Run Docker container
```

### Docker Development

```bash
# Build locally
docker build -t wealthfolio-mcp .

# Run with hot reload for development
docker run -p 8000:8000 -v $(pwd):/app --env-file .env wealthfolio-mcp
```

### Adding New Features

1. Extend the `WealthfolioClient` class in `api_client.py`
2. Add new endpoints in `mcp_server.py`
3. Update the README with new functionality
4. Add tests for new features
5. Update the Dockerfile if new dependencies are added

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

## Releases and Versioning

This project uses automated semantic versioning starting from `0.1.0`. Each push to the `main` branch automatically:

1. Increments the patch version (e.g., `0.1.0` → `0.1.1`)
2. Creates a new GitHub release
3. Builds and pushes Docker images to GitHub Container Registry

### Latest Release

[![GitHub release](https://img.shields.io/github/release/toomy1992/Wealthfolio-MCP.svg)](https://github.com/toomy1992/Wealthfolio-MCP/releases)
[![Docker Image](https://img.shields.io/badge/docker-ghcr.io%2Ftoomy1992%2Fwealthfolio--mcp-blue)](https://github.com/toomy1992/Wealthfolio-MCP/pkgs/container/wealthfolio-mcp)

## Changelog

### v0.2.0
- Added detailed holdings data for accurate rebalancing calculations
- Implemented holdings fallback fetching when bulk endpoint unavailable
- Enhanced portfolio endpoint with comprehensive holdings information
- Added concurrent API fetching for improved performance
- Expanded test coverage for holdings functionality
- Updated documentation with anonymized holdings examples

### v0.1.0
- Initial release
- Wealthfolio API integration with real endpoints
- FastAPI MCP server implementation
- Docker containerization
- OpenWebUI compatibility
- n8n workflow support
- Automated CI/CD with GitHub Actions
- Comprehensive test suite