from sqlalchemy import Column, Integer, String, BigInteger
from sqlalchemy.orm import relationship
from app.models.base import Base  # Base 应在 base.py 中正确声明

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, comment='用户ID')
    email = Column(String(128), unique=True, index=True, nullable=False, comment='邮箱')
    username = Column(String(128), unique=True, index=True, nullable=False, comment='用户名')
    password_hash = Column(String(128), nullable=False, comment='密码哈希')
    
    # 关系定义
    health_data = relationship("HealthData", back_populates="user", cascade="all, delete-orphan")
    exercise_logs = relationship("ExerciseLog", back_populates="user", cascade="all, delete-orphan")
    sleep_records = relationship("SleepRecord", back_populates="user", cascade="all, delete-orphan")
    health_goals = relationship("HealthGoal", back_populates="user", cascade="all, delete-orphan")
    symptom_records = relationship("SymptomRecord", back_populates="user", cascade="all, delete-orphan")