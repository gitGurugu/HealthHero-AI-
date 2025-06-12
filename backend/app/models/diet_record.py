from sqlalchemy import Column, Integer, BigInteger, Date, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base

class DietRecord(Base):
    __tablename__ = "diet_record"
    
    record_id = Column(Integer, primary_key=True, index=True, comment='记录ID')
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, comment='用户ID')
    record_date = Column(Date, nullable=False, comment='记录日期')
    calories = Column(Integer, comment='卡路里')
    food_detail = Column(Text, comment='食物详情')
    
    # 添加约束检查
    __table_args__ = (
        CheckConstraint('calories >= 0', name='check_calories_positive'),
    )
    
    # 与用户表的关系
    user = relationship("User", back_populates="diet_records") 