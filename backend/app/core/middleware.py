import time
from typing import Callable

from fastapi import FastAPI, Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    请求日志中间件
    
    记录每个请求的详细信息，包括：
    - 请求方法
    - 请求路径
    - 响应状态码
    - 处理时间
    - 客户端IP
    - 用户代理
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # 获取请求信息
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # 处理请求
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            status_code = response.status_code
            
            # 记录成功请求
            logger.info(
                f"{method} {path} {status_code} {process_time:.3f}s - IP: {client_ip} - UA: {user_agent}"
            )
            
            return response
        except Exception as e:
            process_time = time.time() - start_time
            
            # 记录异常请求
            logger.error(
                f"{method} {path} 500 {process_time:.3f}s - IP: {client_ip} - UA: {user_agent} - Error: {str(e)}"
            )
            
            raise


class ExceptionMiddleware(BaseHTTPMiddleware):
    """
    异常处理中间件
    
    捕获所有未处理的异常，并记录详细信息
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            # 记录异常详细信息
            logger.exception(f"未处理的异常: {str(e)}")
            
            # 继续抛出异常，让FastAPI的异常处理器处理
            raise


def setup_middlewares(app: FastAPI) -> None:
    """
    设置中间件
    """
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(ExceptionMiddleware)