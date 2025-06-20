from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ExerciseLogCreate(BaseModel):
    user_id: int
    exercise_type: str
    duration_minutes: int
    log_date: datetime

class ExerciseLogResponse(ExerciseLogCreate):
    log_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 