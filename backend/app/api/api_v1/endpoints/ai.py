import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ai_service import AIAssistant
from app.schemas.ai_message import ChatMessage, ChatResponse
logger = logging.getLogger(__name__)

router = APIRouter()
ai_assistant = AIAssistant()

class ChatRequest(BaseModel):
    message: str

class HealthKnowledge(BaseModel):
    content: str
    source: str = None

@router.post("/chat")
async def chat(request: ChatRequest):
    """与 AI 助手对话"""
    try:
        response = await ai_assistant.get_response(request.message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/knowledge")
async def add_knowledge(knowledge: HealthKnowledge):
    """添加新的健康知识"""
    success = await ai_assistant.add_health_knowledge(
        knowledge.content, 
        knowledge.source
    )
    if not success:
        raise HTTPException(status_code=500, detail="添加知识失败")
    return {"message": "成功添加新知识"}




