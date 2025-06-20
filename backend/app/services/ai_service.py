from openai import AsyncOpenAI
from app.core.config import settings
from app.services.rag_factory import get_rag_service
from app.services.base import AIBase
import logging
from fastapi import HTTPException
from typing import Optional, Dict
import importlib
import httpx

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AIAssistant(AIBase):
    def __init__(self):
        # 设置 OpenAI API 配置
        base_url = settings.OPENAI_BASE_URL.rstrip('/')
        if not base_url.endswith('/v1'):
            base_url = f"{base_url}/v1"
        
        # 创建带超时配置的HTTP客户端
        http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0)  # 总超时30秒，连接超时10秒
        )
            
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=base_url,
            http_client=http_client
        )
        
        # 使用RAG工厂获取最优的RAG服务
        self.rag = get_rag_service()
        
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

    async def get_response_stream(self, message: str, user_data: Optional[Dict] = None):
        """
        获取流式 AI 回答
        """
        try:
            logger.info(f"开始流式响应处理，消息: {message[:50]}...")
            
            # 如果有用户数据，使用 HealthAgent 处理
            if user_data is not None:
                logger.info("使用 HealthAgent 处理用户数据")
                async for chunk in self.health_agent.process_request_stream(message, user_data):
                    yield chunk
                return

            # 否则使用普通的 RAG 处理
            logger.info("使用普通 RAG 处理")
            similar_docs = await self.rag.search_similar(message, k=3)
            logger.info(f"找到 {len(similar_docs)} 个相关文档")
            
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
            
            logger.info("开始调用 OpenAI 流式 API")
            
            # 使用流式响应
            stream = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=800,
                stream=True
            )
            
            logger.info("成功创建流式响应")
            chunk_count = 0
            
            async for chunk in stream:
                chunk_count += 1
                logger.debug(f"处理第 {chunk_count} 个流式块")
                
                # 安全地访问流式数据
                if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                    choice = chunk.choices[0]
                    if hasattr(choice, 'delta') and hasattr(choice.delta, 'content'):
                        content = choice.delta.content
                        if content is not None:
                            logger.debug(f"输出内容块: {content[:20]}...")
                            yield content
                else:
                    logger.debug(f"跳过空块: {chunk}")
            
            logger.info(f"流式响应完成，共处理 {chunk_count} 个块")
            
        except Exception as e:
            logger.error(f"AI 流式服务调用失败: {str(e)}", exc_info=True)
            # 返回错误信息而不是抛出异常
            yield f"抱歉，AI服务暂时不可用: {str(e)}"

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



