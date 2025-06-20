from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import setup_middlewares
from app.db.init_db import init_db
from app.db.session import get_db
from fastapi.staticfiles import StaticFiles

# 设置日志
setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="健康管理系统api",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)#实例化一个app对象，传入一些参数

# 设置中间件
setup_middlewares(app)

# 设置CORS
# if settings.BACKEND_CORS_ORIGINS:
#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"],
#     )


# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)
# 包含API路由
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {"message": "欢迎来到健康管理系统系统"}


@app.on_event("startup")
async def startup_event():
    """
    应用程序启动时执行的操作
    """
    db = next(get_db())
    # next() 函数用于从生成器中获取下一个值。如果生成器已经耗尽（即没有更多的值可以返回），next() 会抛出一个 StopIteration 异常。
    init_db(db)


    
# # 添加静态文件服务
# app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)