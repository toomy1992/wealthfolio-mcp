import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from config.settings import settings

class WealthfolioClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = settings.API_BASE_URL

    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make HTTP request to Wealthfolio API"""
        url = f"{self.base_url}{endpoint}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                print(f"HTTP error: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                print(f"Error fetching data: {e}")
                raise

    async def get_accounts(self) -> List[Dict[str, Any]]:
        """Get all accounts"""
        return await self._make_request("/accounts")

    async def get_latest_valuations(self, account_ids: List[str]) -> List[Dict[str, Any]]:
        """Get latest valuations for specified accounts"""
        params = {f"accountIds[]": account_id for account_id in account_ids}
        return await self._make_request("/valuations/latest", params)

    async def get_assets(self) -> List[Dict[str, Any]]:
        """Get all assets"""
        return await self._make_request("/assets")

    async def get_valuation_history(self, account_id: str = "TOTAL", days: int = 30) -> List[Dict[str, Any]]:
        """Get historical valuations"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        params = {
            "accountId": account_id,
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat()
        }
        return await self._make_request("/valuations/history", params)

    async def get_holding_item(self, account_id: str, asset_id: str) -> Optional[Dict[str, Any]]:
        """Get specific holding item"""
        params = {"accountId": account_id, "assetId": asset_id}
        try:
            return await self._make_request("/holdings/item", params)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    async def fetch_portfolio_data(self, filters: dict) -> Dict[str, Any]:
        """Fetch comprehensive portfolio data"""
        try:
            # Get accounts
            accounts = await self.get_accounts()

            # Get latest valuations for all accounts
            account_ids = [acc["id"] for acc in accounts]
            valuations = await self.get_latest_valuations(account_ids)

            # Get assets
            assets = await self.get_assets()

            # Get historical valuations (last 30 days)
            history = await self.get_valuation_history()

            # Calculate totals
            total_value = sum(v.get("totalValue", 0) for v in valuations)
            total_cost = sum(v.get("costBasis", 0) for v in valuations)
            total_contribution = sum(v.get("netContribution", 0) for v in valuations)

            return {
                "accounts": accounts,
                "valuations": valuations,
                "assets": assets,
                "history": history,
                "summary": {
                    "total_value": total_value,
                    "total_cost": total_cost,
                    "total_contribution": total_contribution,
                    "total_gain_loss": total_value - total_cost,
                    "total_gain_loss_percent": ((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0
                }
            }

        except Exception as e:
            print(f"Error fetching portfolio data: {e}")
            # Return mock data for testing
            return {
                "accounts": [],
                "valuations": [],
                "assets": [],
                "history": [],
                "summary": {
                    "total_value": 0,
                    "total_cost": 0,
                    "total_contribution": 0,
                    "total_gain_loss": 0,
                    "total_gain_loss_percent": 0
                }
            }