from pydantic import BaseModel, field_validator
from datetime import datetime, date, time
from typing import Optional, Union
from decimal import Decimal

class SleepRecordCreate(BaseModel):
    user_id: int
    sleep_date: date
    bedtime: datetime
    wake_time: datetime
    sleep_duration: Optional[float] = None
    sleep_quality: Optional[int] = None  # 1-10评分
    deep_sleep_hours: Optional[float] = None
    notes: Optional[str] = None

class SleepRecordResponse(BaseModel):
    sleep_id: int
    user_id: int
    sleep_date: Union[date, datetime]
    bedtime: Union[datetime, time, None] = None
    wake_time: Union[datetime, time, None] = None
    sleep_duration: Optional[Union[float, Decimal]] = None
    sleep_quality: Optional[int] = None
    deep_sleep_hours: Optional[Union[float, Decimal]] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @field_validator('sleep_date', mode='before')
    @classmethod
    def validate_sleep_date(cls, v):
        if isinstance(v, datetime):
            return v.date()
        return v

    @field_validator('sleep_duration', 'deep_sleep_hours', mode='before')
    @classmethod
    def validate_decimal_fields(cls, v):
        if isinstance(v, Decimal):
            return float(v)
        return v

    class Config:
        from_attributes = True 