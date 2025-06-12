from sqlalchemy import Column, Integer, BigInteger, Date, DECIMAL, SmallInteger, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base

class HealthData(Base):
    __tablename__ = "health_data"
    
    record_id = Column(Integer, primary_key=True, index=True, comment='记录ID')
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, comment='用户ID')
    record_date = Column(Date, nullable=False, comment='记录日期')
    height = Column(DECIMAL(5, 2), comment='身高(cm)')
    weight = Column(DECIMAL(5, 1), comment='体重(kg)')
    systolic_pressure = Column(SmallInteger, comment='收缩压')
    diastolic_pressure = Column(SmallInteger, comment='舒张压')
    blood_sugar = Column(DECIMAL(4, 1), comment='血糖')
    cholesterol = Column(DECIMAL(4, 1), comment='胆固醇')
    
    # 添加约束检查
    __table_args__ = (
        CheckConstraint('height > 0', name='check_height_positive'),
        CheckConstraint('weight BETWEEN 30 AND 300', name='check_weight_range'),
        CheckConstraint('systolic_pressure BETWEEN 50 AND 250', name='check_systolic_range'),
        CheckConstraint('diastolic_pressure BETWEEN 30 AND 150', name='check_diastolic_range'),
        CheckConstraint('cholesterol >= 0', name='check_cholesterol_positive'),
    )
    
    # 与用户表的关系
    user = relationship("User", back_populates="health_data") 