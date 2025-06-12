from sqlalchemy import Column, Integer, ForeignKey, String, Date, SmallInteger, Text, DECIMAL
from sqlalchemy.orm import relationship
from .base import Base


class SymptomRecord(Base):
    __tablename__ = "symptom_records"

    symptom_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    record_date = Column(Date, nullable=False)
    symptom_type = Column(String(100), nullable=False)  # 头痛、发烧、咳嗽等
    severity = Column(SmallInteger, nullable=False)  # 1-10严重程度
    description = Column(Text, nullable=True)
    duration_hours = Column(DECIMAL(precision=4, scale=1), nullable=True)  # 持续时间
    location = Column(String(100), nullable=True)  # 症状部位
    triggers = Column(Text, nullable=True)  # 可能的触发因素

    # 关系
    user = relationship("User", back_populates="symptom_records")

    __table_args__ = (
        {"comment": "用户症状记录表"}
    ) 