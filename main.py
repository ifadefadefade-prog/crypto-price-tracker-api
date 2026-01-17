from fastapi import FastAPI
from app.routers import users, prices, token, subscriptions

from app.routers.admin import token as token_admin
from app.routers.admin import users as users_admin

app = FastAPI(title="Crypto Price Tracker API")
app.include_router(users.router)
app.include_router(prices.router)
app.include_router(token.router)
app.include_router(subscriptions.router)
app.include_router(token_admin.router)
app.include_router(users_admin.router)
