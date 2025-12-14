import pytest
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