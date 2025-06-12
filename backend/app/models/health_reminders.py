from sqlalchemy import Column, Integer, ForeignKey, String, Text, Time, Boolean, Enum
from sqlalchemy.orm import relationship
import enum
from .base import Base


class ReminderFrequency(enum.Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class ReminderType(enum.Enum):
    MEDICATION = "medication"
    EXERCISE = "exercise"
    MEAL = "meal"
    WATER = "water"
    SLEEP = "sleep"
    CHECKUP = "checkup"
    MEASUREMENT = "measurement"
    OTHER = "other"


class HealthReminder(Base):
    __tablename__ = "health_reminders"

    reminder_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reminder_type = Column(Enum(ReminderType), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    reminder_time = Column(Time, nullable=False)
    frequency = Column(Enum(ReminderFrequency), nullable=False, default=ReminderFrequency.DAILY)
    days_of_week = Column(String(20), nullable=True)  # "1,2,3,4,5" 表示周一到周五
    is_active = Column(Boolean, nullable=False, default=True)
    custom_interval_days = Column(Integer, nullable=True)  # 自定义间隔天数

    # 关系
    user = relationship("User", back_populates="health_reminders")

    __table_args__ = (
        {"comment": "用户健康提醒表"}
    ) 