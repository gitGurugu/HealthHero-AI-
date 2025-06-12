from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 构建数据库URL时确保密码正确编码
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    echo=True,
    connect_args={
        "options": "-c search_path=public"
    }
)

# 初始化数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 依赖项，用于获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 


# 生成器是一种特殊的迭代器，它可以通过 yield 关键字生成一系列值。生成器函数每次调用时，会从上次暂停的地方继续执行，直到遇到下一个 yield 语句。