from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_KEY: str = "mock_api_key"  # Default for testing
    API_BASE_URL: str = "https://wealthfolio.labruntipi.io/api/v1"
    asset_filters: list[str] = ["stocks", "crypto"]

    model_config = {"env_file": ".env"}

settings = Settings()