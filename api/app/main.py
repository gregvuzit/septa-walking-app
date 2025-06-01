from fastapi import FastAPI
from app.routers.api_router import ApiRouter

app = FastAPI()

app.include_router(ApiRouter, prefix="/api")

@app.exception_handler(404)
async def custom_404_handler(request, exc):
    return {
        "status_code": 404,
        "detail": "The requested URL was not found on the server"
    }