from langchain_openai import OpenAIEmbeddings
from app.core.config import settings
from app.models.vector_store import VectorStore
from sqlalchemy.orm import Session
from app.db.session import engine
import numpy as np
import json
import logging
import asyncio
from typing import List, Dict, Optional
import time
from functools import lru_cache
import hashlib

logger = logging.getLogger(__name__)

class OptimizedRAGService:
    def __init__(self):
        # 修复 API URL
        base_url = settings.OPENAI_BASE_URL.rstrip('/')
        if not base_url.endswith('/v1'):
            base_url = f"{base_url}/v1"
            
        logger.info(f"初始化优化 RAG 服务，使用 API URL: {base_url}")
        
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=base_url,
            model="text-embedding-ada-002"
        )
        
        # 缓存机制
        self._embedding_cache = {}
        self._vector_cache = None
        self._cache_timestamp = 0
        self._cache_ttl = getattr(settings, 'RAG_CACHE_TTL', 300)  # 5分钟缓存
        
        # 预定义的健康知识库（避免每次查询API）
        self.health_knowledge_base = [
            {
                "content": "健康饮食应该包含多样化的食物，包括蔬菜、水果、全谷物、瘦肉蛋白和健康脂肪。建议每天摄入5-9份蔬菜和水果，选择全谷物而非精制谷物，限制加工食品和高糖食品的摄入。均衡的营养摄入有助于维持健康体重、增强免疫力、预防慢性疾病。",
                "source": "营养指南",
                "keywords": ["饮食", "营养", "蔬菜", "水果", "健康食品", "均衡", "维生素"]
            },
            {
                "content": "规律运动对健康至关重要。成年人每周应进行至少150分钟中等强度有氧运动，或75分钟高强度有氧运动，同时每周进行2次或以上肌肉强化活动。运动可以改善心血管健康、增强免疫力、控制体重、改善心情、增强骨密度。",
                "source": "运动指南",
                "keywords": ["运动", "锻炼", "有氧", "肌肉", "健身", "体重", "心血管", "骨密度"]
            },
            {
                "content": "良好的睡眠对健康不可或缺。成年人每晚需要7-9小时的优质睡眠。保持规律的作息时间、创造舒适的睡眠环境、避免睡前使用电子设备、限制咖啡因摄入都有助于改善睡眠质量。充足的睡眠有助于记忆巩固、免疫系统恢复、情绪调节。",
                "source": "睡眠指南",
                "keywords": ["睡眠", "作息", "失眠", "休息", "睡眠质量", "记忆", "免疫", "情绪"]
            },
            {
                "content": "心理健康同样重要。管理压力、保持社交联系、培养兴趣爱好、寻求专业帮助都是维护心理健康的有效方法。冥想、深呼吸、瑜伽等放松技巧可以帮助缓解压力和焦虑。保持积极的心态和良好的人际关系对心理健康至关重要。",
                "source": "心理健康指南",
                "keywords": ["心理", "压力", "焦虑", "冥想", "放松", "情绪", "社交", "人际关系"]
            },
            {
                "content": "定期体检和健康监测有助于早期发现和预防疾病。建议成年人每年进行一次全面体检，包括血压、血糖、胆固醇检查。女性应定期进行乳腺和宫颈癌筛查，男性应关注前列腺健康。预防胜于治疗，早期发现问题可以大大提高治疗效果。",
                "source": "预防医学指南",
                "keywords": ["体检", "预防", "筛查", "血压", "血糖", "胆固醇", "癌症", "早期发现"]
            },
            {
                "content": "水分摄入对健康至关重要。成年人每天应饮用8-10杯水（约2-2.5升）。充足的水分有助于维持体温、润滑关节、运输营养物质、排除废物。运动时或炎热天气下需要增加水分摄入。避免过量饮用含糖饮料和酒精。",
                "source": "水分补充指南",
                "keywords": ["水分", "饮水", "补水", "脱水", "体温", "关节", "营养", "废物"]
            }
        ]

    def _get_query_hash(self, query: str) -> str:
        """生成查询的哈希值用于缓存"""
        return hashlib.md5(query.encode('utf-8')).hexdigest()

    async def _get_cached_embedding(self, text: str) -> Optional[np.ndarray]:
        """获取缓存的embedding"""
        text_hash = self._get_query_hash(text)
        if text_hash in self._embedding_cache:
            logger.debug(f"使用缓存的embedding: {text[:30]}...")
            return self._embedding_cache[text_hash]
        return None

    async def _cache_embedding(self, text: str, embedding: np.ndarray):
        """缓存embedding"""
        text_hash = self._get_query_hash(text)
        self._embedding_cache[text_hash] = embedding
        logger.debug(f"缓存embedding: {text[:30]}...")

    def _keyword_search(self, query: str, k: int = 3) -> List[Dict]:
        """基于关键词的快速搜索（备用方案）"""
        query_lower = query.lower()
        results = []
        
        for item in self.health_knowledge_base:
            score = 0
            # 检查关键词匹配
            for keyword in item["keywords"]:
                if keyword in query_lower:
                    score += 2  # 关键词匹配权重更高
            
            # 检查内容匹配
            content_words = query_lower.split()
            for word in content_words:
                if len(word) > 2 and word in item["content"].lower():
                    score += 1
            
            if score > 0:
                results.append({
                    "content": item["content"],
                    "similarity": score,
                    "source": item["source"]
                })
        
        # 按分数排序并返回前k个结果
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:k]

    async def search_similar_fast(self, query: str, k: int = 2) -> List[Dict]:
        """快速搜索相似内容（优化版本）"""
        start_time = time.time()
        
        try:
            # 1. 首先尝试关键词搜索（最快）
            if getattr(settings, 'RAG_ENABLE_KEYWORD_SEARCH', True):
                keyword_results = self._keyword_search(query, k)
                if keyword_results and keyword_results[0]["similarity"] >= 2:  # 高质量匹配
                    logger.info(f"关键词搜索完成，耗时: {time.time() - start_time:.3f}s")
                    return keyword_results
            
            # 2. 如果关键词搜索无高质量结果，尝试缓存的向量搜索
            cached_embedding = await self._get_cached_embedding(query)
            if cached_embedding is not None:
                vector_results = await self._vector_search_with_embedding(cached_embedding, k)
                if vector_results:
                    logger.info(f"缓存向量搜索完成，耗时: {time.time() - start_time:.3f}s")
                    return vector_results
            
            # 3. 最后才调用API生成新的embedding
            logger.info("生成新的embedding...")
            query_embedding = np.array(await self.embeddings.aembed_query(query))
            await self._cache_embedding(query, query_embedding)
            
            vector_results = await self._vector_search_with_embedding(query_embedding, k)
            if vector_results:
                logger.info(f"新向量搜索完成，总耗时: {time.time() - start_time:.3f}s")
                return vector_results
            
            # 4. 如果向量搜索也失败，返回关键词搜索结果
            logger.warning("向量搜索失败，降级到关键词搜索")
            return self._keyword_search(query, k)
            
        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            # 降级到关键词搜索
            return self._keyword_search(query, k)

    async def _vector_search_with_embedding(self, query_embedding: np.ndarray, k: int) -> List[Dict]:
        """使用已有embedding进行向量搜索"""
        try:
            # 检查缓存是否过期
            current_time = time.time()
            if (self._vector_cache is None or 
                current_time - self._cache_timestamp > self._cache_ttl):
                await self._refresh_vector_cache()
            
            if not self._vector_cache:
                logger.warning("向量缓存为空")
                return []
            
            similarities = []
            
            # 计算相似度
            for vec_data in self._vector_cache:
                stored_vector = vec_data["embedding"]
                similarity = np.dot(query_embedding, stored_vector) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(stored_vector)
                )
                similarities.append({
                    "content": vec_data["content"],
                    "similarity": float(similarity),
                    "source": vec_data["source"]
                })
            
            # 排序并返回前k个结果
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            return similarities[:k]
            
        except Exception as e:
            logger.error(f"向量搜索失败: {str(e)}")
            return []

    async def _refresh_vector_cache(self):
        """刷新向量缓存"""
        try:
            logger.info("刷新向量缓存...")
            with Session(engine) as session:
                vectors = session.query(VectorStore).all()
                self._vector_cache = []
                
                for vec in vectors:
                    try:
                        embedding = np.array(json.loads(vec.embedding))
                        self._vector_cache.append({
                            "content": vec.content,
                            "embedding": embedding,
                            "source": vec.source
                        })
                    except Exception as e:
                        logger.warning(f"跳过无效向量: {e}")
                
                self._cache_timestamp = time.time()
                logger.info(f"向量缓存刷新完成，共加载 {len(self._vector_cache)} 个向量")
                
        except Exception as e:
            logger.error(f"刷新向量缓存失败: {str(e)}")
            self._vector_cache = []

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
                
                # 清除缓存以便下次刷新
                self._vector_cache = None
                return True
                
        except Exception as e:
            logger.error(f"存储向量失败: {str(e)}")
            return False

    # 保持向后兼容
    async def search_similar(self, query: str, k: int = 2):
        """搜索相似内容（兼容接口）"""
        return await self.search_similar_fast(query, k)