# Wealthfolio MCP - Agent Integration Guide

## Overview

**Wealthfolio MCP** is a universal **Model Context Protocol (MCP)** server that exposes Wealthfolio portfolio management API through standardized OpenAPI/REST endpoints. It's designed to be seamlessly integrated with AI agents, OpenWebUI, n8n workflows, and any other MCP-compatible tools.

This document explains the architecture, integration patterns, and how to use this MCP server with agents and AI systems.

---

## Development Workflow for Agents

### Contributing Changes

When making changes to this project, all agents (AI or otherwise) must follow this workflow:

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/description-of-change
   # or
   git checkout -b fix/description-of-bug
   ```

2. **Follow Conventional Commits**
   - `feat:` - New features (bumps MINOR version)
   - `fix:` - Bug fixes (bumps PATCH version)
   - `BREAKING CHANGE:` - Breaking changes (bumps MAJOR version)
   
   **Examples:**
   ```
   feat(api): add new endpoint for sector analysis
   fix(client): resolve null valuation handling
   docs(readme): update installation instructions
   chore(deps): upgrade fastapi dependency
   ```

3. **Submit Pull Request**
   - Create PR from feature branch to `main`
   - Use descriptive title and description
   - Link to any related issues
   - Ensure tests pass and linting succeeds

4. **Merge and Release**
   - PR review and approval
   - Merge to main triggers CI/CD pipeline
   - Pipeline analyzes Conventional Commits
   - Automatic version bump (MAJOR.MINOR.PATCH)
   - Docker image tagged with version
   - Release created with changelog

### Automated Version Management

The CI/CD workflow automatically determines version increments:

```
Commit message with "BREAKING CHANGE:" → v1.0.0 → v2.0.0 (MAJOR)
Commit message with "feat:" prefix     → v1.0.0 → v1.1.0 (MINOR)
Commit message with "fix:" prefix      → v1.0.0 → v1.0.1 (PATCH)
```

### Docker Image Versioning

Docker images are tagged with the exact semantic version:
- ✅ `ghcr.io/toomy1992/wealthfolio-mcp:v1.0.0`
- ❌ `ghcr.io/toomy1992/wealthfolio-mcp:latest` (deprecated)

Pull the correct version:
```bash
docker pull ghcr.io/toomy1992/wealthfolio-mcp:v1.0.0
```

---

## Table of Contents

1. [Development Workflow for Agents](#development-workflow-for-agents)
2. [Architecture](#architecture)
3. [MCP Protocol Support](#mcp-protocol-support)
4. [OpenAPI Integration](#openapi-integration)
5. [Integration Patterns](#integration-patterns)
6. [Available Tools/Functions](#available-toolsfunctions)
7. [Example Agent Workflows](#example-agent-workflows)
8. [Deployment Patterns](#deployment-patterns)
9. [Security & Authentication](#security--authentication)

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Agent / OpenWebUI                      │
│              (Claude, GPT-4, Grok, or other LLM)             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTP/REST Calls
                     │
┌────────────────────▼────────────────────────────────────────┐
│         MCP-to-OpenAPI Proxy Server (mcpo)                  │
│   - Auto-discovers MCP tools                                │
│   - Converts to REST endpoints                              │
│   - Generates OpenAPI documentation                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ stdio/HTTP
                     │
┌────────────────────▼────────────────────────────────────────┐
│        Wealthfolio MCP Server (FastAPI)                     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ OpenAPI Endpoints:                                   │  │
│  │  - GET /accounts                                     │  │
│  │  - GET /assets                                       │  │
│  │  - GET /valuations/latest                            │  │
│  │  - GET /valuations/history                           │  │
│  │  - GET /holdings/item                                │  │
│  │  - GET /portfolio (aggregate)                        │  │
│  │  - POST /sync                                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                     │                                        │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │      WealthfolioClient                               │  │
│  │  (API Client with helper methods)                    │  │
│  │                                                      │  │
│  │  - _make_request()                                   │  │
│  │  - get_accounts()                                    │  │
│  │  - get_latest_valuations()                           │  │
│  │  - get_assets()                                      │  │
│  │  - get_valuation_history()                           │  │
│  │  - get_holding_item()                                │  │
│  │  - fetch_portfolio_data()                            │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTP
                     │
┌────────────────────▼────────────────────────────────────────┐
│          Wealthfolio API                                    │
│   (https://wealthfolio.labruntipi.io/api/v1)               │
└─────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
wealthfolio-mcp/
├── src/
│   ├── mcp_server.py           # FastAPI MCP server with OpenAPI endpoints
│   └── api_client.py            # Wealthfolio API client wrapper
├── config/
│   └── settings.py              # Configuration & environment variables
├── tests/
│   ├── __init__.py
│   └── test_api_client.py       # Unit tests
├── .github/workflows/           # CI/CD pipelines
├── Dockerfile                   # Docker containerization
├── docker-compose.yml           # Local development setup
├── requirements.txt             # Python dependencies
├── Makefile                     # Development commands
├── README.md                    # Project overview
├── AGENTS.md                    # This file
└── .env.example                 # Environment template
```

### Core Files

#### `src/mcp_server.py`
- **FastAPI application** serving as MCP server
- **OpenAPI endpoint definitions** with auto-generated documentation
- **Error handling** and HTTP status management
- Integrates with `WealthfolioClient` for data fetching

**Key Features:**
- Custom OpenAPI schema generation
- Detailed docstrings for each endpoint (explaining which client methods are used)
- Tags and categorization for better API organization
- Automatic Swagger/OpenAPI documentation at `/docs` and `/openapi.json`

#### `src/api_client.py`
- **WealthfolioClient class** - wrapper around Wealthfolio API
- **Async HTTP client** using `httpx` for non-blocking I/O
- **Core methods**:
  - `_make_request()` - Core HTTP handler
  - `get_accounts()` - Fetch all accounts
  - `get_latest_valuations()` - Get current valuations
  - `get_assets()` - Get asset information
  - `get_valuation_history()` - Get historical data
  - `get_holding_item()` - Get specific holdings
  - `fetch_portfolio_data()` - Aggregate comprehensive portfolio data

#### `config/settings.py`
- **Pydantic Settings** for environment configuration
- **Environment variables**:
  - `API_KEY` - Wealthfolio API authentication
  - `API_BASE_URL` - API endpoint URL
  - `asset_filters` - Asset type filtering

---

## MCP Protocol Support

### What is MCP?

**Model Context Protocol (MCP)** is an open standard for connecting AI models and applications to external tools and data sources. It's maintained by Anthropic and Hugging Face.

**Key Benefits:**
- Standardized tool interface for AI agents
- No vendor lock-in
- Works with Claude, ChatGPT, local LLMs, and more
- Seamless integration with platforms like OpenWebUI

### MCP Implementation in This Project

This project uses **FastAPI + mcpo proxy** to implement MCP:

1. **FastAPI Server** (`src/mcp_server.py`):
   - Provides REST endpoints that expose portfolio data
   - Auto-generates OpenAPI documentation
   - Handles async operations efficiently

2. **mcpo Proxy Layer**:
   - Converts MCP protocol to REST/HTTP
   - Discovers available tools dynamically
   - Auto-generates interactive API documentation
   - Enables cloud deployment without stdio limitations

### MCP Tool Definitions

The server exposes these **MCP-compatible tools**:

| Tool | Endpoint | Method | Description |
|------|----------|--------|-------------|
| `get_accounts` | `/accounts` | GET | Fetch all accounts |
| `get_assets` | `/assets` | GET | Fetch all assets |
| `get_latest_valuations` | `/valuations/latest` | GET | Get current valuations |
| `get_valuation_history` | `/valuations/history` | GET | Get historical data |
| `get_holding_item` | `/holdings/item` | GET | Get specific holdings |
| `fetch_portfolio_data` | `/portfolio` | GET | Comprehensive portfolio data |
| `sync_portfolio` | `/sync` | POST | Trigger synchronization |

---

## OpenAPI Integration

### Why OpenAPI?

OpenAPI (formerly Swagger) provides:
- **Standard API documentation** that's machine-readable
- **Auto-generated client SDKs** for multiple languages
- **Interactive testing** via Swagger UI
- **Integration with API gateways** and reverse proxies
- **Compatibility with API management tools**

### Accessing OpenAPI Documentation

The server automatically generates OpenAPI 3.0 documentation:

**Interactive Swagger UI:**
```
http://localhost:8000/docs
```

**OpenAPI JSON Schema:**
```
http://localhost:8000/openapi.json
```

### Custom OpenAPI Schema

The server includes a custom `custom_openapi()` function that:
- Defines comprehensive API metadata
- Explains data sources and client methods used
- Documents integration capabilities
- Provides usage examples

---

## Integration Patterns

### Pattern 1: Direct REST API Calls

**Use Case:** Simple scripts, webhooks, or automation tools that need direct HTTP access

```bash
# Get portfolio summary
curl -X GET "http://localhost:8000/portfolio" \
  -H "accept: application/json"

# Get specific account valuations
curl -X GET "http://localhost:8000/valuations/latest?account_ids=acc1&account_ids=acc2" \
  -H "accept: application/json"
```

**Pros:**
- Simple and direct
- No protocol overhead
- Easy debugging

**Cons:**
- No semantic understanding by agents
- Requires manual parsing of responses

### Pattern 2: MCP via mcpo Proxy (Recommended)

**Use Case:** AI agents (Claude, GPT-4, local LLMs) integrated with OpenWebUI

```bash
# Install mcpo
pip install mcpo

# Run MCP server through OpenAPI proxy
mcpo --host 0.0.0.0 --port 8000 -- uvicorn src.mcp_server:app --host 127.0.0.1 --port 8001
```

**How it works:**
1. mcpo proxy listens on port 8000 (HTTP)
2. FastAPI server runs on port 8001 (internal)
3. mcpo discovers endpoints and converts them to MCP tools
4. Agent calls tools via MCP protocol
5. mcpo translates to REST calls to FastAPI
6. Results returned to agent

**Pros:**
- Semantic tool understanding by agents
- Automatic tool discovery
- Works with any MCP-compatible platform
- Cloud-friendly (no stdio limitations)
- Auto-generated documentation

**Cons:**
- Additional proxy layer
- Slight latency increase

### Pattern 3: OpenWebUI Plugin

**Use Case:** Using portfolio data within OpenWebUI chat interface

**Steps:**

1. **Install OpenWebUI MCP Plugin**
   - Navigate to OpenWebUI settings
   - Go to Tools/Plugins
   - Add custom server

2. **Configure server URL:**
   ```
   http://localhost:8000/openapi.json
   ```

3. **Enable tools in chat:**
   - Tools become available in chat interface
   - Agent can call them contextually
   - Responses are integrated into conversation

4. **Example agent interaction:**
   ```
   User: "What's my current portfolio value?"
   
   Agent: Uses /portfolio tool
   Response: "Your total portfolio value is $150,000..."
   ```

### Pattern 4: n8n Workflow Integration

**Use Case:** Automated portfolio monitoring and reporting

```
[Trigger: Every day at 9 AM]
    ↓
[HTTP Node: GET /portfolio]
    ↓
[Data Transform: Calculate gains/losses]
    ↓
[IF: Significant change?]
    ├─→ [Yes] → [Send Email/Slack notification]
    └─→ [No] → [Log to database]
```

**Configuration:**
- **HTTP Node URL:** `http://localhost:8000/portfolio`
- **Method:** GET
- **Response:** Automatically parsed JSON

---

## Available Tools/Functions

### 1. Get Accounts
**Endpoint:** `GET /accounts`  
**MCP Tool:** `get_accounts()`  
**Client Method:** `client.get_accounts()`

```python
# Returns list of account dictionaries
[
    {
        "id": "account-123",
        "name": "Main Portfolio",
        "currency": "USD",
        "isActive": true
    }
]
```

### 2. Get Assets
**Endpoint:** `GET /assets`  
**MCP Tool:** `get_assets()`  
**Client Method:** `client.get_assets()`

```python
# Returns list of available assets
[
    {
        "id": "AAPL",
        "name": "Apple Inc.",
        "type": "stock",
        "exchange": "NASDAQ"
    }
]
```

### 3. Get Latest Valuations
**Endpoint:** `GET /valuations/latest?account_ids=acc1,acc2`  
**MCP Tool:** `get_latest_valuations(account_ids)`  
**Client Method:** `client.get_latest_valuations(account_ids)`

```python
# Returns current valuations for specified accounts
[
    {
        "accountId": "acc1",
        "totalValue": 50000.00,
        "costBasis": 45000.00,
        "gain": 5000.00
    }
]
```

### 4. Get Valuation History
**Endpoint:** `GET /valuations/history?account_id=TOTAL&days=30`  
**MCP Tool:** `get_valuation_history(account_id, days)`  
**Client Method:** `client.get_valuation_history(account_id, days)`

```python
# Returns historical valuations for specified period
[
    {
        "date": "2025-12-11",
        "value": 150000.00
    },
    {
        "date": "2025-12-10",
        "value": 149500.00
    }
]
```

### 5. Get Holding Item
**Endpoint:** `GET /holdings/item?account_id=acc1&asset_id=AAPL`  
**MCP Tool:** `get_holding_item(account_id, asset_id)`  
**Client Method:** `client.get_holding_item(account_id, asset_id)`

```python
# Returns specific holding details
{
    "accountId": "acc1",
    "assetId": "AAPL",
    "quantity": 100,
    "purchasePrice": 150.00,
    "currentPrice": 170.00,
    "totalValue": 17000.00
}
```

### 6. Get Portfolio (Aggregate)
**Endpoint:** `GET /portfolio`  
**MCP Tool:** `fetch_portfolio_data()`  
**Client Methods:** Uses all above methods

```python
# Comprehensive portfolio data combining all sources
{
    "accounts": [...],
    "valuations": [...],
    "assets": [...],
    "history": [...],
    "summary": {
        "total_value": 150000.00,
        "total_cost": 120000.00,
        "total_contribution": 130000.00,
        "total_gain_loss": 30000.00,
        "total_gain_loss_percent": 25.0
    }
}
```

### 7. Sync Portfolio
**Endpoint:** `POST /sync`  
**MCP Tool:** `sync_portfolio()`  
**Client Method:** N/A (placeholder)

```python
# Placeholder for future sync implementation
{
    "message": "Synchronization triggered."
}
```

---

## Example Agent Workflows

### Workflow 1: Portfolio Analysis Assistant

**Scenario:** Agent analyzes portfolio and provides insights

```
User: "Analyze my portfolio and tell me where I should rebalance"

Agent Actions:
1. Call /portfolio → Get comprehensive portfolio data
2. Call /valuation_history?days=90 → Get 3-month trend
3. Call /assets → Get available assets
4. Analyze data:
   - Calculate sector allocation
   - Identify underperforming assets
   - Compare to risk tolerance
5. Recommend rebalancing actions
```

**Example Agent Prompt:**
```
You are a financial advisor. You have access to portfolio data via the Wealthfolio MCP server.
User asked: "Analyze my portfolio"

Available tools:
- get_portfolio() - Get complete portfolio with all accounts and valuations
- get_valuation_history(days=30) - Get historical performance
- get_accounts() - List all accounts

Steps:
1. Fetch portfolio data
2. Analyze allocation
3. Compare to benchmarks
4. Provide recommendations
```

### Workflow 2: Daily Portfolio Report

**Scenario:** Automated agent generates daily reports

```
Trigger: Daily at 9 AM

Agent Actions:
1. Call /portfolio → Get current status
2. Calculate daily changes
3. Identify notable movements
4. Generate report:
   - Total value
   - Daily gains/losses
   - Top performers
   - Top losers
5. Send via email/Slack
```

### Workflow 3: Portfolio Alert System

**Scenario:** Agent monitors for significant changes

```
Trigger: Every hour

Agent Actions:
1. Call /portfolio → Get current valuations
2. Compare with previous hour:
   - If change > 5% → Alert
   - If change > 10% → Critical alert
3. Identify which assets changed
4. Send notification with details

Tool: get_latest_valuations()
```

### Workflow 4: Asset Research Assistant

**Scenario:** Agent helps research potential investments

```
User: "I want to invest in tech stocks. What tech stocks do I already have?"

Agent Actions:
1. Call /assets → Get all available assets
2. Filter for type="stock" and sector="tech"
3. Call /portfolio → Check holdings
4. Show current tech holdings
5. Provide research recommendations
6. Compare with available tech assets
```

---

## Deployment Patterns

### Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure .env
cp .env.example .env
# Edit API_KEY and API_BASE_URL

# 3. Run server
make dev
# or: uvicorn src.mcp_server:app --reload
```

**Access:**
- Server: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

### Docker Standalone

```bash
# Build
docker build -t wealthfolio-mcp .

# Run
docker run -p 8000:8000 \
  -e API_KEY=your_key \
  -e API_BASE_URL=https://wealthfolio.labruntipi.io/api/v1 \
  wealthfolio-mcp
```

### Docker Compose (Recommended)

```bash
# 1. Configure .env
cp .env.example .env

# 2. Run
docker-compose up -d

# 3. Access
# Server: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### MCP + mcpo in Production

**Docker Compose with mcpo:**

```yaml
version: '3.8'

services:
  mcp-proxy:
    image: python:3.11-slim
    working_dir: /app
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - API_KEY=${API_KEY}
      - API_BASE_URL=${API_BASE_URL}
    command: >
      sh -c "pip install mcpo uvicorn -q &&
             python -m uvicorn src.mcp_server:app --host 127.0.0.1 --port 8001 &
             mcpo --host 0.0.0.0 --port 8000 -- uvicorn src.mcp_server:app --host 127.0.0.1 --port 8001"
```

### Cloud Deployment

**AWS ECS/Fargate:**
- Container image: `ghcr.io/toomy1992/wealthfolio-mcp:latest`
- Environment variables: API_KEY, API_BASE_URL
- Port: 8000
- Health check: `GET /portfolio`

**Railway/Render/Heroku:**
```bash
# Push image
docker tag wealthfolio-mcp your-registry/wealthfolio-mcp
docker push your-registry/wealthfolio-mcp

# Deploy with environment variables
# API_KEY, API_BASE_URL
```

---

## Security & Authentication

### API Key Management

**Environment Variables:**
```bash
# .env file (keep confidential)
API_KEY=your_wealthfolio_api_key_here
API_BASE_URL=https://wealthfolio.labruntipi.io/api/v1
```

**Best Practices:**
1. Never commit `.env` to version control
2. Use `.env.example` as template
3. Rotate API keys periodically
4. Use separate keys for dev/prod
5. Store in secure vaults (AWS Secrets Manager, HashiCorp Vault)

### Network Security

**Local Development:**
- Server listens on `127.0.0.1` (loopback only)
- No external access without explicit binding

**Production:**
- Use reverse proxy (nginx, Cloudflare, AWS ALB)
- Enable HTTPS/TLS encryption
- Implement API key validation
- Add rate limiting
- Use network security groups/firewalls

### Container Security

**Docker Best Practices:**
- Non-root user (UID: app)
- Read-only filesystem where possible
- Health checks enabled
- Resource limits defined
- Minimal base image (python:3.11-slim)

### Data Privacy

- Portfolio data is only accessed when explicitly requested
- No data is stored locally (stateless design)
- All data returned from Wealthfolio API
- User responsible for Wealthfolio API security

### Future Authentication

Potential enhancements:
- JWT token support
- OAuth2 integration
- API key rotation mechanisms
- Rate limiting by key
- Audit logging

---

## Advanced Usage

### Custom Agent Implementation

**Python with `anthropic` SDK:**

```python
from anthropic import Anthropic
import httpx

client = Anthropic()

# Define portfolio tools
tools = [
    {
        "name": "get_portfolio",
        "description": "Get comprehensive portfolio data",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_valuation_history",
        "description": "Get historical valuations",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Number of days to retrieve",
                    "default": 30
                }
            }
        }
    }
]

# Agent loop
messages = []
while True:
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        tools=tools,
        messages=messages
    )
    
    # Handle tool calls
    for block in response.content:
        if block.type == "tool_use":
            tool_name = block.name
            tool_input = block.input
            
            # Call portfolio server
            if tool_name == "get_portfolio":
                result = httpx.get("http://localhost:8000/portfolio").json()
            elif tool_name == "get_valuation_history":
                days = tool_input.get("days", 30)
                result = httpx.get(
                    f"http://localhost:8000/valuations/history?days={days}"
                ).json()
            
            # Continue conversation with results
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result)
                    }
                ]
            })
```

### Extending Wealthfolio Client

Add custom methods to `WealthfolioClient`:

```python
# In src/api_client.py

async def calculate_performance(self, account_id: str = "TOTAL") -> Dict[str, Any]:
    """Calculate performance metrics for account"""
    valuations = await self.get_latest_valuations([account_id])
    history = await self.get_valuation_history(account_id, days=365)
    
    return {
        "current_value": valuations[0]["totalValue"],
        "annual_gain": calculate_annual_gain(history),
        "volatility": calculate_volatility(history)
    }

async def get_sector_allocation(self, account_id: str = "TOTAL") -> Dict[str, float]:
    """Get portfolio allocation by sector"""
    assets = await self.get_assets()
    valuations = await self.get_latest_valuations([account_id])
    # Calculate sector allocation
    ...
```

### Custom OpenAPI Extensions

Add OpenAPI vendors extensions for better documentation:

```python
# In src/mcp_server.py

openapi_schema["servers"] = [
    {
        "url": "http://localhost:8000",
        "description": "Local development server"
    },
    {
        "url": "https://api.wealthfolio.example.com",
        "description": "Production server"
    }
]

openapi_schema["components"]["securitySchemes"] = {
    "api_key": {
        "type": "apiKey",
        "name": "API_KEY",
        "in": "header"
    }
}
```

---

## Troubleshooting

### Common Issues

**1. "Cannot connect to Wealthfolio API"**
- Check API_KEY and API_BASE_URL in .env
- Verify network connectivity
- Check Wealthfolio API status

**2. "ModuleNotFoundError: No module named 'fastapi'"**
```bash
pip install -r requirements.txt
```

**3. "Port 8000 already in use"**
```bash
# Use different port
uvicorn src.mcp_server:app --port 8001
```

**4. "401 Unauthorized from Wealthfolio API"**
- Invalid or expired API key
- Contact Wealthfolio support for new key

**5. "Empty response from /portfolio"**
- Check Wealthfolio account has data
- Verify asset_filters in .env
- Check API response in browser: http://localhost:8000/docs

### Debug Mode

```bash
# Run with debug logging
DEBUG=1 uvicorn src.mcp_server:app --reload --log-level debug
```

---

## Resources

### Official Documentation
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [mcpo GitHub Repository](https://github.com/open-webui/mcpo)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAPI Specification](https://www.openapis.org/)

### Related Projects
- [Open WebUI](https://openwebui.com/)
- [Anthropic Claude](https://www.anthropic.com/)
- [n8n Workflows](https://n8n.io/)

### Support
- GitHub Issues: [toomy1992/Wealthfolio-MCP](https://github.com/toomy1992/Wealthfolio-MCP)
- OpenWebUI Discord: [Community](https://discord.gg/5rJgQTnV4s)
- MCP Community: [GitHub Discussions](https://github.com/modelcontextprotocol/servers/discussions)

---

## Contributing

Contributions are welcome! Areas for enhancement:

- [ ] Additional MCP tools (sector analysis, rebalancing recommendations)
- [ ] Caching layer for performance
- [ ] WebSocket support for real-time updates
- [ ] Database persistence for historical tracking
- [ ] Advanced authentication (OAuth2, JWT)
- [ ] Multi-user support with isolation
- [ ] Portfolio comparison tools
- [ ] Tax reporting integration

See [GitHub Issues](https://github.com/toomy1992/Wealthfolio-MCP/issues) for current work.

---

## License

This project is open source. See LICENSE file for details.

---

## Version History

- **v1.0.0** (2026-01-11)
  - Initial release with OpenAPI support
  - MCP protocol compatibility
  - mcpo proxy integration ready
  - 7 core portfolio endpoints
  - Comprehensive documentation
