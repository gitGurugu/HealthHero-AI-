from fastapi import APIRouter

from app.api.api_v1.endpoints import ai
from app.api.api_v1.endpoints import users
from app.api.api_v1.endpoints import health_data
from app.api.api_v1.endpoints import exercise_log, health_goals, sleep_record, symptom_records
from app.api.api_v1.endpoints import rag
from app.api.api_v1.endpoints import health_analytics

api_router = APIRouter()

api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(rag.router, prefix="/rag", tags=["rag"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(health_data.router, prefix="/health-data", tags=["健康数据"])
api_router.include_router(health_analytics.router, prefix="/health-analytics", tags=["健康分析"])
api_router.include_router(exercise_log.router, prefix="/exercise-log", tags=["运动记录"])
api_router.include_router(health_goals.router, prefix="/health-goals", tags=["健康目标"])
api_router.include_router(sleep_record.router, prefix="/sleep-record", tags=["睡眠记录"])
api_router.include_router(symptom_records.router, prefix="/symptom-records", tags=["症状记录"])


