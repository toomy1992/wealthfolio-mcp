import pytest
import httpx
from unittest.mock import AsyncMock, patch
from src.api_client import WealthfolioClient


class TestWealthfolioClient:
    """Test cases for Wealthfolio API client"""

    @pytest.fixture
    def client(self):
        """Create a test client instance"""
        return WealthfolioClient(api_key="test_key")

    @pytest.mark.asyncio
    async def test_get_accounts_success(self, client):
        """Test successful account retrieval"""
        mock_response = [
            {
                "id": "test-account-1",
                "name": "Test Account",
                "currency": "USD",
                "isActive": True
            }
        ]

        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await client.get_accounts()

            assert result == mock_response
            mock_request.assert_called_once_with("/accounts")

    @pytest.mark.asyncio
    async def test_get_latest_valuations_success(self, client):
        """Test successful valuation retrieval"""
        account_ids = ["acc1", "acc2"]
        mock_response = [
            {
                "accountId": "acc1",
                "totalValue": 10000.0,
                "cashBalance": 1000.0
            }
        ]

        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await client.get_latest_valuations(account_ids)

            assert result == mock_response
            mock_request.assert_called_once_with("/valuations/latest", {"accountIds[]": ["acc1", "acc2"]})

    @pytest.mark.asyncio
    async def test_fetch_portfolio_data_success(self, client):
        """Test successful portfolio data fetching"""
        with patch.object(client, 'get_accounts', new_callable=AsyncMock) as mock_accounts, \
             patch.object(client, 'get_latest_valuations', new_callable=AsyncMock) as mock_valuations, \
             patch.object(client, 'get_assets', new_callable=AsyncMock) as mock_assets, \
             patch.object(client, 'get_valuation_history', new_callable=AsyncMock) as mock_history:

            mock_accounts.return_value = [{"id": "acc1", "name": "Test Account"}]
            mock_valuations.return_value = [{"accountId": "acc1", "totalValue": 10000.0, "costBasis": 9000.0, "netContribution": 8000.0}]
            mock_assets.return_value = [{"id": "AAPL", "name": "Apple Inc."}]
            mock_history.return_value = [{"date": "2025-12-14", "totalValue": 10000.0}]

            result = await client.fetch_portfolio_data({})

            assert "accounts" in result
            assert "valuations" in result
            assert "assets" in result
            assert "history" in result
            assert "summary" in result

            # Check summary calculations
            summary = result["summary"]
            assert summary["total_value"] == 10000.0
            assert summary["total_cost"] == 9000.0
            assert summary["total_contribution"] == 8000.0
            assert summary["total_gain_loss"] == 1000.0
            assert summary["total_gain_loss_percent"] == pytest.approx(11.11, rel=1e-2)

    @pytest.mark.asyncio
    async def test_fetch_portfolio_data_error_handling(self, client):
        """Test error handling in portfolio data fetching"""
        with patch.object(client, 'get_accounts', new_callable=AsyncMock) as mock_accounts:
            mock_accounts.side_effect = Exception("API Error")

            result = await client.fetch_portfolio_data({})

            # Should return mock data on error
            assert result["summary"]["total_value"] == 0
            assert result["accounts"] == []
            assert result["valuations"] == []
            assert result["assets"] == []
            assert result["history"] == []

    @pytest.mark.asyncio
    async def test_get_holding_item_success(self, client):
        """Test successful holding item retrieval"""
        mock_response = {
            "accountId": "acc1",
            "assetId": "AAPL",
            "quantity": 100,
            "purchasePrice": 150.00,
            "currentPrice": 170.00,
            "totalValue": 17000.00,
            "costBasis": 15000.00,
            "gainLoss": 2000.00
        }

        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await client.get_holding_item("acc1", "AAPL")

            assert result == mock_response
            mock_request.assert_called_once_with("/holdings/item", {"accountId": "acc1", "assetId": "AAPL"})

    @pytest.mark.asyncio
    async def test_get_holding_item_not_found(self, client):
        """Test holding item not found returns None"""
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = httpx.HTTPStatusError(
                "Not Found", request=None, response=httpx.Response(404)
            )

            result = await client.get_holding_item("acc1", "INVALID")

            assert result is None
            mock_request.assert_called_once_with("/holdings/item", {"accountId": "acc1", "assetId": "INVALID"})

    @pytest.mark.asyncio
    async def test_get_holdings_bulk_success(self, client):
        """Test successful bulk holdings retrieval"""
        account_ids = ["acc1", "acc2"]
        mock_response = [
            {
                "accountId": "acc1",
                "assetId": "AAPL",
                "quantity": 100,
                "purchasePrice": 150.00,
                "currentPrice": 170.00,
                "totalValue": 17000.00
            }
        ]

        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await client.get_holdings(account_ids)

            assert result == mock_response
            mock_request.assert_called_once_with("/holdings", {"accountIds[]": account_ids})

    @pytest.mark.asyncio
    async def test_get_holdings_fallback(self, client):
        """Test holdings fallback when bulk endpoint fails"""
        account_ids = ["acc1"]

        # Mock assets response
        mock_assets = [
            {"id": "AAPL", "type": "stock"},
            {"id": "CASH", "type": "CASH"},  # Should be filtered out
            {"id": "EUR", "type": "FOREX"}   # Should be filtered out
        ]

        # Mock holding response for AAPL
        mock_holding = {
            "accountId": "acc1",
            "assetId": "AAPL",
            "quantity": 100,
            "purchasePrice": 150.00,
            "currentPrice": 170.00,
            "totalValue": 17000.00
        }

        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request, \
             patch.object(client, 'get_assets', new_callable=AsyncMock) as mock_get_assets, \
             patch.object(client, 'get_holding_item', new_callable=AsyncMock) as mock_get_holding:

            # Bulk endpoint fails with 404
            mock_request.side_effect = httpx.HTTPStatusError(
                "Not Found", request=None, response=httpx.Response(404)
            )
            mock_get_assets.return_value = mock_assets
            mock_get_holding.return_value = mock_holding

            result = await client.get_holdings(account_ids)

            assert len(result) == 1
            assert result[0] == mock_holding
            # Should call get_holding_item for AAPL only (CASH and FOREX filtered out)
            mock_get_holding.assert_called_once_with("acc1", "AAPL")

    @pytest.mark.asyncio
    async def test_get_holdings_empty_accounts(self, client):
        """Test get_holdings with empty account list"""
        result = await client.get_holdings([])
        assert result == []