from fastapi import FastAPI
from src.api_client import WealthfolioClient
from config.settings import settings

app = FastAPI()

client = WealthfolioClient(api_key=settings.API_KEY)

@app.get("/portfolio")
async def get_portfolio():
    filters = {"assets": settings.asset_filters}
    data = await client.fetch_portfolio_data(filters=filters)
    return data

@app.post("/sync")
async def sync_portfolio():
    # Placeholder for synchronization logic
    return {"message": "Synchronization triggered."}