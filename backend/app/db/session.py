from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# 构建数据库URL时确保密码正确编码
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    echo=False,  # 关闭SQL日志以减少噪音
    connect_args={
        "options": "-c search_path=public"
    },
    # 添加连接池配置
    pool_size=5,  # 减少连接池大小
    max_overflow=10,  # 减少最大溢出连接
    pool_recycle=1800,  # 30分钟回收连接
    pool_timeout=30,
    pool_reset_on_return='commit'  # 连接返回时提交事务
)

# 初始化数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 依赖项，用于获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"数据库操作异常: {str(e)}")
        db.rollback()
        raise e
    except Exception as e:
        logger.error(f"未知异常: {str(e)}")
        logger.error(f"异常类型: {type(e).__name__}")
        logger.error(f"异常详情: {repr(e)}")
        db.rollback()
        raise e
    finally:
        db.close()

# 生成器是一种特殊的迭代器，它可以通过 yield 关键字生成一系列值。生成器函数每次调用时，会从上次暂停的地方继续执行，直到遇到下一个 yield 语句。