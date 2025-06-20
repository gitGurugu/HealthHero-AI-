"""
RAG服务管理和监控接口
"""

import logging
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag_factory import get_rag_service, RAGFactory, reset_rag_service
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

router = APIRouter()

class RAGTestRequest(BaseModel):
    query: str
    k: int = 2

class RAGTestResponse(BaseModel):
    query: str
    results: List[Dict[str, Any]]
    duration: float
    service_type: str

@router.get("/info")
async def get_rag_info():
    """获取RAG服务信息"""
    try:
        performance_info = RAGFactory.get_performance_info()
        rag_service = get_rag_service()
        
        return {
            "status": "active",
            "service_class": type(rag_service).__name__,
            "performance_info": performance_info
        }
    except Exception as e:
        logger.error(f"获取RAG信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test", response_model=RAGTestResponse)
async def test_rag_search(request: RAGTestRequest):
    """测试RAG搜索性能"""
    try:
        rag_service = get_rag_service()
        
        start_time = time.time()
        
        # 根据服务类型选择搜索方法
        if hasattr(rag_service, 'search_similar_fast'):
            results = await rag_service.search_similar_fast(request.query, request.k)
        else:
            results = await rag_service.search_similar(request.query, request.k)
        
        duration = time.time() - start_time
        
        return RAGTestResponse(
            query=request.query,
            results=results,
            duration=duration,
            service_type=type(rag_service).__name__
        )
        
    except Exception as e:
        logger.error(f"RAG搜索测试失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/benchmark")
async def benchmark_rag():
    """RAG性能基准测试"""
    try:
        test_queries = [
            "什么是健康饮食？",
            "如何保持良好的睡眠？",
            "运动对健康有什么好处？",
            "怎样管理压力？",
            "定期体检的重要性"
        ]
        
        rag_service = get_rag_service()
        results = []
        total_time = 0
        
        for query in test_queries:
            start_time = time.time()
            
            if hasattr(rag_service, 'search_similar_fast'):
                search_results = await rag_service.search_similar_fast(query, 2)
            else:
                search_results = await rag_service.search_similar(query, 2)
            
            duration = time.time() - start_time
            total_time += duration
            
            results.append({
                "query": query,
                "duration": duration,
                "result_count": len(search_results),
                "results": search_results
            })
        
        avg_time = total_time / len(test_queries)
        
        return {
            "service_type": type(rag_service).__name__,
            "total_queries": len(test_queries),
            "total_time": total_time,
            "average_time": avg_time,
            "results": results,
            "performance_rating": "excellent" if avg_time < 0.1 else "good" if avg_time < 0.5 else "needs_improvement"
        }
        
    except Exception as e:
        logger.error(f"RAG基准测试失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset")
async def reset_rag():
    """重置RAG服务实例"""
    try:
        reset_rag_service()
        new_service = get_rag_service()
        
        return {
            "message": "RAG服务已重置",
            "new_service_type": type(new_service).__name__
        }
        
    except Exception as e:
        logger.error(f"重置RAG服务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cache/stats")
async def get_cache_stats():
    """获取缓存统计信息"""
    try:
        rag_service = get_rag_service()
        
        if hasattr(rag_service, '_embedding_cache'):
            cache_size = len(rag_service._embedding_cache)
            vector_cache_size = len(rag_service._vector_cache) if rag_service._vector_cache else 0
            
            return {
                "embedding_cache_size": cache_size,
                "vector_cache_size": vector_cache_size,
                "cache_ttl": getattr(rag_service, '_cache_ttl', 0),
                "last_cache_refresh": getattr(rag_service, '_cache_timestamp', 0)
            }
        else:
            return {
                "message": "当前RAG服务不支持缓存统计",
                "service_type": type(rag_service).__name__
            }
            
    except Exception as e:
        logger.error(f"获取缓存统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cache/clear")
async def clear_cache():
    """清空RAG缓存"""
    try:
        rag_service = get_rag_service()
        
        if hasattr(rag_service, '_embedding_cache'):
            rag_service._embedding_cache.clear()
            rag_service._vector_cache = None
            rag_service._cache_timestamp = 0
            
            return {
                "message": "RAG缓存已清空",
                "service_type": type(rag_service).__name__
            }
        else:
            return {
                "message": "当前RAG服务不支持缓存清空",
                "service_type": type(rag_service).__name__
            }
            
    except Exception as e:
        logger.error(f"清空RAG缓存失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 