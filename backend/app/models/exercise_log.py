from sqlalchemy import Column, Integer, BigInteger, Date, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base

class ExerciseLog(Base):
    __tablename__ = "exercise_log"
    
    log_id = Column(Integer, primary_key=True, index=True, comment='日志ID')
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, comment='用户ID')
    exercise_type = Column(String(50), comment='运动类型')
    duration_minutes = Column(Integer, comment='运动时长(分钟)')
    log_date = Column(Date, nullable=False, comment='日志日期')
    
    # 添加约束检查
    __table_args__ = (
        CheckConstraint('duration_minutes > 0', name='check_duration_positive'),
    )
    
    # 与用户表的关系
    user = relationship("User", back_populates="exercise_logs") 