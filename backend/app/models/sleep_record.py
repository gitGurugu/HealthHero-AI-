from sqlalchemy import Column, Integer, ForeignKey, Date, DateTime, DECIMAL, SmallInteger, Text
from sqlalchemy.orm import relationship
from .base import Base


class SleepRecord(Base):
    __tablename__ = "sleep_records"

    sleep_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sleep_date = Column(Date, nullable=False)
    bedtime = Column(DateTime, nullable=True)
    wake_time = Column(DateTime, nullable=True)
    sleep_duration = Column(DECIMAL(precision=3, scale=1), nullable=True)  # 小时
    sleep_quality = Column(SmallInteger, nullable=True)  # 1-10评分
    deep_sleep_hours = Column(DECIMAL(precision=3, scale=1), nullable=True)
    notes = Column(Text, nullable=True)

    # 关系
    user = relationship("User", back_populates="sleep_records")

    __table_args__ = (
        {"comment": "用户睡眠记录表"}
    ) 