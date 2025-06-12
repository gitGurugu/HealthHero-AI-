from langchain_openai import OpenAIEmbeddings
from app.core.config import settings
from app.models.vector_store import VectorStore
from sqlalchemy.orm import Session
from app.db.session import engine
import numpy as np
import json
import logging

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        # 修复 API URL
        base_url = settings.OPENAI_BASE_URL.rstrip('/')
        if not base_url.endswith('/v1'):
            base_url = f"{base_url}/v1"
            
        logger.info(f"初始化 RAG 服务，使用 API URL: {base_url}")
        
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=base_url,  # 这里使用已经处理好的 base_url
            model="text-embedding-ada-002"
        )

    async def store_vector(self, content: str, source: str = None):
        """存储向量到数据库"""
        try:
            # 生成文本的向量表示
            embedding = await self.embeddings.aembed_query(content)
            
            # 存储到向量数据库
            with Session(engine) as session:
                vector_store = VectorStore(
                    content=content,
                    embedding=json.dumps(embedding),
                    source=source
                )
                session.add(vector_store)
                session.commit()
                logger.info(f"成功存储向量: {content[:50]}...")
                return True
                
        except Exception as e:
            logger.error(f"存储向量失败: {str(e)}")
            return False

    async def search_similar(self, query: str, k: int = 2):
        """搜索相似内容并返回结果"""
        try:
            # 1. 将输入文本转换为向量
            query_embedding = np.array(await self.embeddings.aembed_query(query))
            
            # 2. 在向量库中搜索相似内容
            with Session(engine) as session:
                vectors = session.query(VectorStore).all()
                similarities = []
                
                # 3. 计算相似度
                for vec in vectors:
                    stored_vector = np.array(json.loads(vec.embedding))
                    similarity = np.dot(query_embedding, stored_vector) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(stored_vector)
                    )
                    similarities.append((vec, similarity))
                
                # 4. 返回最相似的结果
                similarities.sort(key=lambda x: x[1], reverse=True)
                return [
                    {
                        "content": vec.content,
                        "similarity": float(sim),
                        "source": vec.source
                    }
                    for vec, sim in similarities[:k]
                ]
                
        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            return []