from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    API_KEY: str = "mock_api_key"  # Default for testing
    API_BASE_URL: str = "https://wealthfolio.labruntipi.io/api/v1"
    asset_filters: Optional[str] = None  # JSON string from env, parsed as needed

    model_config = {"env_file": ".env"}

settings = Settings()