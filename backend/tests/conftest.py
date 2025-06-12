import os
from typing import Dict, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.session import Base
from app.main import app
from app.services import user_service
from app.schemas.user import UserCreate

# 使用测试数据库
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db() -> Generator:
    """
    创建测试数据库会话
    """
    # 创建测试数据库表
    Base.metadata.create_all(bind=engine)
    
    # 创建会话
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        # 删除测试数据库
        os.remove("./test.db")


@pytest.fixture(scope="session")
def client(db: Session) -> Generator:
    """
    创建测试客户端
    """
    # 使用测试数据库会话
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    # 替换依赖项
    app.dependency_overrides = {get_db: override_get_db}
    
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def superuser(db: Session) -> Dict[str, str]:
    """
    创建超级用户
    """
    user_in = UserCreate(
        email="admin@test.com",
        username="admin",
        password="admin",
        is_superuser=True,
    )
    user = user_service.get_user_by_email(db, email=user_in.email)
    if not user:
        user = user_service.create_user(db, obj_in=user_in)
    
    return {
        "email": user_in.email,
        "password": user_in.password,
    } 