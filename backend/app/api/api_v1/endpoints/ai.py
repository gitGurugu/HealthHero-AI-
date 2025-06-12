import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.ai_service import AIAssistant
from typing import Optional, List
from app.schemas.ai_message import ChatMessage, ChatResponse

logger = logging.getLogger(__name__)

router = APIRouter()
ai_assistant = AIAssistant()

# 基础对话相关模型
class BasicChatRequest(BaseModel):
    message: str = Field(..., description="用户问题")

# 健康咨询相关模型
class SleepSchedule(BaseModel):
    bedtime: Optional[str] = Field(None, description="就寝时间，格式：HH:MM")
    wake_time: Optional[str] = Field(None, description="起床时间，格式：HH:MM")

class UserHealthData(BaseModel):
    age: Optional[int] = Field(None, description="年龄")
    height: Optional[float] = Field(None, description="身高(cm)")
    weight: Optional[float] = Field(None, description="体重(kg)")
    diet_records: Optional[List[str]] = Field(None, description="饮食记录")
    exercise_contraindications: Optional[str] = Field(None, description="运动禁忌")
    avg_sleep_hours: Optional[float] = Field(None, description="平均睡眠时长")
    sleep_issues: Optional[List[str]] = Field(None, description="睡眠问题列表")
    sleep_schedule: Optional[SleepSchedule] = Field(None, description="作息时间")

class HealthChatRequest(BaseModel):
    message: str = Field(..., description="健康咨询问题")
    user_data: UserHealthData = Field(..., description="用户健康数据")

class HealthKnowledge(BaseModel):
    content: str
    source: str = None

@router.post("/chat", response_model=ChatResponse)
async def basic_chat(request: BasicChatRequest):
    """普通对话接口：用于一般性问题咨询"""
    try:
        response = await ai_assistant.get_response(
            message=request.message
        )
        return ChatResponse(
            code=0,
            data={"response": response},
            msg="success"
        )
    except Exception as e:
        logger.error(f"对话失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/health/chat", response_model=ChatResponse)
async def health_chat(request: HealthChatRequest):
    """健康咨询接口：用于提供个性化健康建议"""
    try:
        response = await ai_assistant.get_response(
            message=request.message,
            user_data=request.user_data.dict(exclude_none=True)
        )
        return ChatResponse(
            code=0,
            data={"response": response},
            msg="success"
        )
    except Exception as e:
        logger.error(f"健康咨询失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/health/knowledge")
async def add_knowledge(knowledge: HealthKnowledge):
    """添加新的健康知识"""
    success = await ai_assistant.add_health_knowledge(
        knowledge.content, 
        knowledge.source
    )
    if not success:
        raise HTTPException(status_code=500, detail="添加知识失败")
    return {"message": "成功添加新知识"}




