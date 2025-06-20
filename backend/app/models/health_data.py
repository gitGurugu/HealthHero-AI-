from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Numeric, SmallInteger
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class HealthData(Base):
    __tablename__ = "health_data"

    record_id = Column(Integer, primary_key=True, index=True)  # 使用实际的主键列名
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    record_date = Column(DateTime, default=datetime.utcnow)  # 使用实际的日期列名
    height = Column(Numeric(5, 2), nullable=True)  # 身高(cm)，使用实际的数据类型
    weight = Column(Numeric(5, 1), nullable=True)  # 体重(kg)，使用实际的数据类型
    systolic_pressure = Column(SmallInteger, nullable=True)  # 收缩压，使用实际的列名
    diastolic_pressure = Column(SmallInteger, nullable=True)  # 舒张压，使用实际的列名
    blood_sugar = Column(Numeric(4, 1), nullable=True)  # 血糖
    cholesterol = Column(Numeric(4, 1), nullable=True)  # 胆固醇
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="health_data")
    
    # 为了向后兼容，添加属性别名
    @property
    def id(self):
        return self.record_id
    
    @property
    def date(self):
        return self.record_date
    
    @property
    def blood_pressure_systolic(self):
        return self.systolic_pressure
    
    @property
    def blood_pressure_diastolic(self):
        return self.diastolic_pressure 