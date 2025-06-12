from fastapi import APIRouter

from app.api.api_v1.endpoints import ai
from app.api.api_v1.endpoints import users



api_router = APIRouter()


api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(users.router, prefix="/users", tags=["users"])


