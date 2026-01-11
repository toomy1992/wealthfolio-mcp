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
    
    Args:
        account_id: The account ID containing the holding
        asset_id: The asset ID of the holding
        
    Returns:
        Dictionary with holding item details from Wealthfolio API, or None if not found
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
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi