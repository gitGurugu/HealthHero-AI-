from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.models.base import Base

class VectorStore(Base):
    __tablename__ = "vector_store"
    
    id = Column(Integer, primary_key=True, index=True, comment='主键ID')
    content = Column(Text, nullable=False, comment='文本内容')
    embedding = Column(Text, nullable=False, comment='向量数据(JSON格式)')
    source = Column(String(255), nullable=True, comment='来源文档')
    meta_info = Column(Text, nullable=True, comment='元数据(JSON格式)')  # 将 metadata 改为 meta_info
    created_at = Column(DateTime, server_default=func.current_timestamp(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.current_timestamp(), 
                       onupdate=func.current_timestamp(), comment='更新时间')