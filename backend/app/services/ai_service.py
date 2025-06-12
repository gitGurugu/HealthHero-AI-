from openai import AsyncOpenAI
from app.core.config import settings
from app.services.rag_service import RAGService
from app.services.base import AIBase
import logging
from fastapi import HTTPException
from typing import Optional, Dict
import importlib

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AIAssistant(AIBase):
    def __init__(self):
        # 设置 OpenAI API 配置
        base_url = settings.OPENAI_BASE_URL.rstrip('/')
        if not base_url.endswith('/v1'):
            base_url = f"{base_url}/v1"
            
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=base_url
        )
        
        # 初始化 RAG 服务
        self.rag = RAGService()
        
        # 延迟导入 HealthAgent
        HealthAgent = importlib.import_module('app.services.health_agent').HealthAgent
        self.health_agent = HealthAgent(self)

        self.system_prompt = """
        你是一个专业的健康助手。请基于提供的参考信息来回答用户的问题。
        如果参考信息不足以完整回答问题，可以补充其他相关的专业知识。
        
        注意事项：
        1. 优先使用参考信息中的内容
        2. 确保回答准确专业
        3. 使用通俗易懂的语言
        4. 给出具体、可执行的建议
        5. 不要提供医疗诊断或治疗建议
        """

    async def get_response(self, message: str, user_data: Optional[Dict] = None) -> str:
        """
        获取 AI 回答，如果提供了用户数据，则使用 HealthAgent 处理
        """
        try:
            # 如果有用户数据，使用 HealthAgent 处理
            if user_data is not None:
                return await self.health_agent.process_request(message, user_data)

            # 否则使用普通的 RAG 处理
            similar_docs = await self.rag.search_similar(message, k=3)
            context = "\n\n".join([
                f"参考信息 {i+1}：{doc['content']}"
                for i, doc in enumerate(similar_docs)
            ])
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"""
参考以下信息：

{context}

用户问题：{message}

请根据以上参考信息和你的专业知识，给出合适的回答。
                """}
            ]
            
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"AI 服务调用失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"AI 服务调用失败: {str(e)}"
            )

    async def add_health_knowledge(self, content: str, source: str = None) -> bool:
        """添加新的健康知识到向量库"""
        try:
            success = await self.rag.store_vector(content, source)
            if success:
                logger.info(f"成功添加新知识: {content[:50]}...")
            return success
        except Exception as e:
            logger.error(f"添加知识失败: {str(e)}")
            return False



