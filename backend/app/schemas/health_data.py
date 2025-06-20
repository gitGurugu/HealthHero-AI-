from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from decimal import Decimal

class HealthDataCreate(BaseModel):
    user_id: int
    record_date: datetime
    height: Optional[Decimal] = None  # 身高(cm)
    weight: Optional[Decimal] = None  # 体重(kg)
    systolic_pressure: Optional[int] = None  # 收缩压
    diastolic_pressure: Optional[int] = None  # 舒张压
    blood_sugar: Optional[Decimal] = None  # 血糖
    cholesterol: Optional[Decimal] = None  # 胆固醇

class HealthDataResponse(BaseModel):
    record_id: int
    user_id: int
    record_date: datetime
    height: Optional[Decimal] = None
    weight: Optional[Decimal] = None
    systolic_pressure: Optional[int] = None
    diastolic_pressure: Optional[int] = None
    blood_sugar: Optional[Decimal] = None
    cholesterol: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime
    
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

    class Config:
        from_attributes = True 