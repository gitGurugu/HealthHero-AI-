from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class HealthGoalsCreate(BaseModel):
    user_id: int
    goal_type: str
    title: str
    description: Optional[str] = None
    target_value: float
    current_value: Optional[float] = None
    unit: str
    start_date: datetime
    target_date: datetime
    status: str = "active"

class HealthGoalsResponse(HealthGoalsCreate):
    goal_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 