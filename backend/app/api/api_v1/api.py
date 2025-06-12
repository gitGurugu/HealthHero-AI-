from fastapi import APIRouter

from app.api.api_v1.endpoints import ai
from app.api.api_v1.endpoints import users
from backend.app.api.api_v1.endpoints import health_data
from backend.app.api.api_v1.endpoints import goals_reminders



api_router = APIRouter()


api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(health_data.router, prefix="/health", tags=["health-data"])
api_router.include_router(goals_reminders.router, prefix="/health", tags=["goals-reminders"])


