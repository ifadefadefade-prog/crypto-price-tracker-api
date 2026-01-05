from fastapi import FastAPI

app = FastAPI(title="Crypto Price Tracker API")


@app.get("/")
async def read_root():
    return {"Hello": "World"}
