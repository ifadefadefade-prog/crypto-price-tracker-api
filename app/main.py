from fastapi import FastAPI
from app.routers import users, prices, token, subscriptions


app = FastAPI(title="Crypto Price Tracker API")
app.include_router(users.router)
app.include_router(prices.router)
app.include_router(token.router)
app.include_router(subscriptions.router)
