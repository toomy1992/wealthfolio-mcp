from fastapi import FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi
from src.api_client import WealthfolioClient
from config.settings import settings
from typing import List, Dict, Any, Optional

app = FastAPI(
    title="Wealthfolio MCP Server",
    description="Universal MCP Server for Wealthfolio Portfolio Management with OpenAPI Integration",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

client = WealthfolioClient(api_key=settings.API_KEY)


@app.get(
    "/accounts",
    tags=["Portfolio Data"],
    summary="Get all accounts",
    responses={200: {"description": "List of all accounts from Wealthfolio API"}},
)
async def get_accounts() -> List[Dict[str, Any]]:
    """
    Fetch all accounts from Wealthfolio API.
    
    Uses: `get_accounts()` from WealthfolioClient
    
    Returns:
        List of account dictionaries containing account details from Wealthfolio
    """
    try:
        return await client.get_accounts()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching accounts: {str(e)}")


@app.get(
    "/valuations/latest",
    tags=["Portfolio Data"],
    summary="Get latest valuations",
    responses={200: {"description": "Latest valuations for specified accounts"}},
)
async def get_latest_valuations(account_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Get latest valuations for specified accounts.
    
    Uses: `get_latest_valuations()` from WealthfolioClient
    
    Args:
        account_ids: List of account IDs to fetch valuations for
        
    Returns:
        List of valuation dictionaries with current values from Wealthfolio API
    """
    try:
        return await client.get_latest_valuations(account_ids)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching valuations: {str(e)}")


@app.get(
    "/assets",
    tags=["Portfolio Data"],
    summary="Get all assets",
    responses={200: {"description": "List of all assets from Wealthfolio"}},
)
async def get_assets() -> List[Dict[str, Any]]:
    """
    Fetch all assets available in Wealthfolio.
    
    Uses: `get_assets()` from WealthfolioClient
    
    Returns:
        List of asset dictionaries with asset information from Wealthfolio API
    """
    try:
        return await client.get_assets()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching assets: {str(e)}")


@app.get(
    "/valuations/history",
    tags=["Portfolio Data"],
    summary="Get valuation history",
    responses={200: {"description": "Historical valuations for specified period"}},
)
async def get_valuation_history(
    account_id: str = "TOTAL",
    days: int = 30
) -> List[Dict[str, Any]]:
    """
    Get historical valuations for a specified account and time period.
    
    Uses: `get_valuation_history()` from WealthfolioClient
    
    Args:
        account_id: Account ID to fetch history for (default: "TOTAL" for all accounts)
        days: Number of days to retrieve history for (default: 30)
        
    Returns:
        List of historical valuation dictionaries from Wealthfolio API
    """
    try:
        return await client.get_valuation_history(account_id=account_id, days=days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching valuation history: {str(e)}")


@app.get(
    "/holdings/item",
    tags=["Portfolio Data"],
    summary="Get specific holding item",
    responses={200: {"description": "Specific holding item details"}},
)
async def get_holding_item(
    account_id: str,
    asset_id: str
) -> Optional[Dict[str, Any]]:
    """
    Get a specific holding item for an account and asset.
    
    Uses: `get_holding_item()` from WealthfolioClient
    
    **Important:** Use the account **UUID** (from `GET /accounts` -> `id` field), NOT the account name.
    
    Example:
    - Account UUID from GET /accounts: "40d73b4b-a731-467c-ae5b-657bea8e52643"
    - Asset ID: "VHYL.GB"
    - Correct request: `/holdings/item?account_id=40d73b4b-a731-467c-ae5b-657bea8e52643&asset_id=VHYL.GB`
    - ❌ WRONG: `/holdings/item?account_id=Boś&asset_id=VHYL.GB` (account name instead of UUID)
    
    Args:
        account_id: The account UUID (unique identifier from GET /accounts -> id field). Must be UUID format, NOT account name
        asset_id: The asset ID/symbol (e.g., "VHYL.GB", "AAPL", "BTC")
        
    Returns:
        Dictionary with holding item details from Wealthfolio API, or 404 error if not found
    """
    try:
        result = await client.get_holding_item(account_id=account_id, asset_id=asset_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Holding item not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching holding item: {str(e)}")


@app.get(
    "/portfolio",
    tags=["Portfolio Data"],
    summary="Get comprehensive portfolio data",
    responses={200: {"description": "Complete portfolio information with accounts, valuations, assets, and summary"}},
)
async def get_portfolio() -> Dict[str, Any]:
    """
    Fetch comprehensive portfolio data including all accounts, valuations, assets, and calculated summary.
    
    This is the main aggregation endpoint that uses multiple WealthfolioClient methods:
    - `get_accounts()` - Fetches all accounts
    - `get_latest_valuations()` - Gets current valuations for all accounts
    - `get_assets()` - Retrieves all available assets
    - `get_valuation_history()` - Gets historical data (last 30 days)
    - `fetch_portfolio_data()` - Aggregates all data with calculated totals
    
    Returns:
        Dictionary containing:
        - accounts: List of all accounts
        - valuations: Latest valuations for each account
        - assets: All available assets
        - history: Historical valuation data
        - summary: Calculated summary with totals, gains/losses, and percentages
    """
    try:
        filters = {"assets": settings.asset_filters}
        data = await client.fetch_portfolio_data(filters=filters)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching portfolio data: {str(e)}")


@app.post(
    "/sync",
    tags=["System"],
    summary="Trigger portfolio synchronization",
    responses={200: {"description": "Synchronization triggered successfully"}},
)
async def sync_portfolio() -> Dict[str, str]:
    """
    Trigger portfolio synchronization (placeholder for future implementation).
    
    This endpoint will be used to force a sync of portfolio data with external sources.
    
    Returns:
        Status message indicating synchronization was triggered
    """
    return {"message": "Synchronization triggered."}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Wealthfolio MCP Server",
        version="1.0.0",
        description="""
## Universal MCP Server for Wealthfolio Portfolio Management

This OpenAPI-compliant server provides comprehensive access to Wealthfolio portfolio data through standardized REST endpoints.

### Key Features:
- **Real-time Portfolio Data**: Fetch current portfolio valuations, holdings, and performance metrics
- **Account Management**: Access all your Wealthfolio accounts and their details
- **Asset Information**: Get comprehensive asset profiles and market data
- **Historical Valuations**: Retrieve portfolio performance history over time
- **MCP Protocol Support**: Compatible with Model Context Protocol for integration with OpenWebUI and other MCP-compatible applications
- **OpenAPI Standard**: Full OpenAPI 3.0 documentation and auto-generated API clients

### Data Sources:
All data is fetched from the Wealthfolio API using the following client methods:
- `_make_request()` - Core HTTP request handler for Wealthfolio API
- `get_accounts()` - Fetches all user accounts
- `get_latest_valuations()` - Gets current account valuations
- `get_assets()` - Retrieves all available assets
- `get_valuation_history()` - Gets historical valuation data
- `get_holding_item()` - Gets specific asset holdings
- `fetch_portfolio_data()` - Aggregates comprehensive portfolio information

### Integration:
This server is designed to work seamlessly with:
- OpenWebUI and its MCP integration via mcpo proxy
- Standard OpenAPI-compatible tools and SDKs
- REST API clients and automation platforms
""",
        routes=app.routes,
    )
    
    openapi_schema["info"]["x-logo"] = {
        "url": "https://wealthfolio.io/assets/logo.png"
    }
    
    # Enhance /holdings/item endpoint parameters with clear documentation
    if "paths" in openapi_schema and "/holdings/item" in openapi_schema["paths"]:
        holdings_item_path = openapi_schema["paths"]["/holdings/item"]
        if "get" in holdings_item_path:
            holdings_item_get = holdings_item_path["get"]
            # Update parameter descriptions to make it clear UUID should be used
            if "parameters" in holdings_item_get:
                for param in holdings_item_get["parameters"]:
                    if param["name"] == "account_id":
                        param["description"] = "Account UUID (from GET /accounts -> id field). MUST be UUID, NOT account name. Example: '40d73b4b-a731-467c-ae5b-657bea8e52643'"
                        param["example"] = "40d73b4b-a731-467c-ae5b-657bea8e52643"
                        param["schema"] = {"type": "string", "format": "uuid", "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"}
                    elif param["name"] == "asset_id":
                        param["description"] = "Asset ID/symbol (e.g., 'VHYL.GB', 'AAPL', 'BTC')"
                        param["example"] = "VHYL.GB"
    
    # Also enhance /valuations/latest endpoint to clarify account IDs
    if "paths" in openapi_schema and "/valuations/latest" in openapi_schema["paths"]:
        valuations_path = openapi_schema["paths"]["/valuations/latest"]
        if "get" in valuations_path:
            valuations_get = valuations_path["get"]
            if "parameters" in valuations_get:
                for param in valuations_get["parameters"]:
                    if param["name"] == "account_ids":
                        param["description"] = "List of account UUIDs (from GET /accounts -> id field). Must be UUIDs, NOT account names"
                        param["example"] = ["40d73b4b-a731-467c-ae5b-657bea8e52643"]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi