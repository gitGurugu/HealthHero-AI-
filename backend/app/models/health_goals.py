from sqlalchemy import Column, Integer, ForeignKey, String, DECIMAL, Date, Enum
from sqlalchemy.orm import relationship
import enum
from .base import Base


class GoalStatus(enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class GoalType(enum.Enum):
    WEIGHT_LOSS = "weight_loss"
    WEIGHT_GAIN = "weight_gain"
    EXERCISE = "exercise"
    DIET = "diet"
    SLEEP = "sleep"
    BLOOD_PRESSURE = "blood_pressure"
    CHOLESTEROL = "cholesterol"
    OTHER = "other"


class HealthGoal(Base):
    __tablename__ = "health_goals"

    goal_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal_type = Column(Enum(GoalType), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    target_value = Column(DECIMAL(precision=8, scale=2), nullable=False)
    current_value = Column(DECIMAL(precision=8, scale=2), nullable=True, default=0)
    unit = Column(String(20), nullable=True)  # kg, hours, steps等
    start_date = Column(Date, nullable=False)
    target_date = Column(Date, nullable=False)
    status = Column(Enum(GoalStatus), nullable=False, default=GoalStatus.ACTIVE)

    # 关系
    user = relationship("User", back_populates="health_goals")

    __table_args__ = (
        {"comment": "用户健康目标表"}
    ) 