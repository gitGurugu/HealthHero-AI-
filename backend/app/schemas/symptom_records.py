from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SymptomRecordsCreate(BaseModel):
    user_id: int
    record_date: datetime
    symptom_type: str
    severity: int  # 1-10评分
    description: Optional[str] = None
    duration_hours: Optional[float] = None
    location: Optional[str] = None
    triggers: Optional[str] = None

class SymptomRecordsResponse(SymptomRecordsCreate):
    symptom_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 