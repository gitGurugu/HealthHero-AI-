import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger
from pydantic import BaseModel


class LoggingConfig(BaseModel):
    """日志配置"""
    LOGGING_LEVEL: str = "INFO"
    LOGGING_FORMAT: str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    LOGGING_ROTATION: str = "500 MB"
    LOGGING_RETENTION: str = "10 days"
    LOGGING_PATH: str = "logs"


class InterceptHandler(logging.Handler):
    """
    拦截标准库日志并将其重定向到loguru
    
    这允许我们捕获所有第三方库的日志
    """

    def emit(self, record: logging.LogRecord) -> None:
        # 获取对应的Loguru级别
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 查找调用者
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging(config: Optional[LoggingConfig] = None) -> None:
    """
    设置日志配置
    
    Args:
        config: 日志配置
    """
    if config is None:
        config = LoggingConfig()

    # 创建日志目录
    Path(config.LOGGING_PATH).mkdir(parents=True, exist_ok=True)

    # 配置loguru
    logger.configure(
        handlers=[
            {
                "sink": sys.stderr,
                "level": config.LOGGING_LEVEL,
                "format": config.LOGGING_FORMAT,
            },
            {
                "sink": f"{config.LOGGING_PATH}/app.log",
                "level": config.LOGGING_LEVEL,
                "format": config.LOGGING_FORMAT,
                "rotation": config.LOGGING_ROTATION,
                "retention": config.LOGGING_RETENTION,
                "compression": "zip",
            },
        ]
    )

    # 拦截标准库日志
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # 拦截第三方库日志
    for logger_name in logging.root.manager.loggerDict:
        logging.getLogger(logger_name).handlers = [InterceptHandler()]

    # 设置uvicorn日志
    for _log in ["uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"]:
        _logger = logging.getLogger(_log)
        _logger.handlers = [InterceptHandler()]

    # 记录启动日志
    logger.info("日志系统已初始化") 

    str='11'
    