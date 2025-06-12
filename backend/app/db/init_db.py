import logging
import hashlib
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import engine
from app.models.base import Base
from app.models.user import User
from datetime import datetime


logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    """
    初始化数据库
    """
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    logger.info("数据库表创建完成")
    
    # 检查是否需要创建测试用户（可选）
    test_user = db.query(User).filter(User.username == "testuser").first()
    if not test_user:
        # 创建测试用户
        password = "password123"  # 测试密码，可根据需求修改
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        test_user = User(
            username="testuser",
            email="test@example.com",  # 添加 email 字段
            password_hash=password_hash,
            created_at=datetime.utcnow(),  # 添加创建时间
            updated_at=datetime.utcnow()   # 添加更新时间
        )
        db.add(test_user)
        db.commit()
        logger.info("测试用户已创建")
    else:
        logger.info("测试用户已存在")