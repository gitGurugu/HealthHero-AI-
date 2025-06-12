from sqlalchemy import Column, Integer, ForeignKey, Date, DECIMAL, Text
from sqlalchemy.orm import relationship
from .base import Base


class BodyMeasurement(Base):
    __tablename__ = "body_measurements"

    measurement_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    measurement_date = Column(Date, nullable=False)
    waist_circumference = Column(DECIMAL(precision=5, scale=1), nullable=True)  # 腰围(cm)
    hip_circumference = Column(DECIMAL(precision=5, scale=1), nullable=True)   # 臀围(cm)
    chest_circumference = Column(DECIMAL(precision=5, scale=1), nullable=True)  # 胸围(cm)
    arm_circumference = Column(DECIMAL(precision=5, scale=1), nullable=True)   # 臂围(cm)
    thigh_circumference = Column(DECIMAL(precision=5, scale=1), nullable=True) # 大腿围(cm)
    body_fat_percentage = Column(DECIMAL(precision=4, scale=1), nullable=True) # 体脂率(%)
    muscle_mass = Column(DECIMAL(precision=5, scale=1), nullable=True)         # 肌肉量(kg)
    bone_density = Column(DECIMAL(precision=4, scale=2), nullable=True)        # 骨密度
    visceral_fat_level = Column(DECIMAL(precision=4, scale=1), nullable=True)  # 内脏脂肪等级
    notes = Column(Text, nullable=True)

    # 关系
    user = relationship("User", back_populates="body_measurements")

    __table_args__ = (
        {"comment": "用户身体测量记录表"}
    ) 