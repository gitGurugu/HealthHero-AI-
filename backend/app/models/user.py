from sqlalchemy import Column, Integer, String
from app.models.base import Base  # Base 应在 base.py 中正确声明

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(128), unique=True, index=True, nullable=False)  # 新增 email 字段
    username = Column(String(128), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)