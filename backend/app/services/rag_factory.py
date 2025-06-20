"""
RAG服务工厂
根据配置和环境选择最合适的RAG服务
"""

from app.core.config import settings
from app.services.rag_service import RAGService
from app.services.rag_service_optimized import OptimizedRAGService
import logging

logger = logging.getLogger(__name__)

class RAGFactory:
    """RAG服务工厂类"""
    
    @staticmethod
    def create_rag_service():
        """创建RAG服务实例"""
        
        if settings.RAG_USE_OPTIMIZED:
            logger.info("使用优化的RAG服务")
            return OptimizedRAGService()
        else:
            logger.info("使用标准RAG服务")
            return RAGService()
    
    @staticmethod
    def get_performance_info():
        """获取当前RAG配置的性能信息"""
        if settings.RAG_USE_OPTIMIZED:
            return {
                "service_type": "optimized",
                "features": [
                    "关键词快速搜索",
                    "Embedding缓存",
                    "向量缓存",
                    "降级搜索策略"
                ],
                "cache_ttl": settings.RAG_CACHE_TTL,
                "keyword_search": settings.RAG_ENABLE_KEYWORD_SEARCH,
                "cache_size": settings.RAG_EMBEDDING_CACHE_SIZE
            }
        else:
            return {
                "service_type": "standard",
                "features": [
                    "标准向量搜索",
                    "实时embedding生成"
                ],
                "cache_ttl": 0,
                "keyword_search": False,
                "cache_size": 0
            }

# 全局RAG服务实例
_rag_instance = None

def get_rag_service():
    """获取RAG服务单例"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGFactory.create_rag_service()
        logger.info(f"创建RAG服务实例: {type(_rag_instance).__name__}")
    return _rag_instance

def reset_rag_service():
    """重置RAG服务实例（用于配置更改后）"""
    global _rag_instance
    _rag_instance = None
    logger.info("RAG服务实例已重置") 