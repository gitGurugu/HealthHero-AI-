import os
from typing import Any, Dict, List, Optional, Union
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # 项目配置
    PROJECT_NAME: str = Field("health", description="项目名称")
    SECRET_KEY: str = Field("changethis", description="密钥")
    BACKEND_CORS_ORIGINS: List[str] = Field(["*"], description="CORS配置")
    
    # 日志配置
    LOGGING_LEVEL: str = Field("DEBUG", description="日志级别")
    LOGGING_PATH: str = Field("logs", description="日志路径")

    # 数据库配置
    POSTGRES_SERVER: str = Field(..., description="PostgreSQL服务器地址")
    POSTGRES_USER: str = Field(..., description="数据库用户名")
    POSTGRES_PASSWORD: str = Field(..., description="数据库密码")
    POSTGRES_DB: str = Field(..., description="数据库名称")
    POSTGRES_PORT: str = Field(..., description="数据库端口")

    # API 配置
    API_V1_STR: str = Field("/api/v1", description="API版本路径")
    
    # JWT 配置
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field( 60*24*6, description="访问令牌过期时间（分钟）")  #30s
    
    # OpenAI 配置
    OPENAI_API_KEY: str = Field(..., description="OpenAI API密钥")
    OPENAI_BASE_URL: str = Field(..., description="OpenAI API基础URL")
    OPENAI_MODEL: str = Field("gpt-3.5-turbo", description="OpenAI模型名称")
    
    # RAG 优化配置
    RAG_USE_OPTIMIZED: bool = Field(True, description="是否使用优化的RAG服务")
    RAG_CACHE_TTL: int = Field(300, description="RAG缓存过期时间（秒）")
    RAG_ENABLE_KEYWORD_SEARCH: bool = Field(True, description="是否启用关键词搜索")
    RAG_EMBEDDING_CACHE_SIZE: int = Field(1000, description="Embedding缓存大小")

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        password = quote_plus(self.POSTGRES_PASSWORD)
        return f"postgresql://{self.POSTGRES_USER}:{password}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

