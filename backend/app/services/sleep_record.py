from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from app.models.sleep_record import SleepRecord
from app.schemas.sleep_record import SleepRecordCreate

class SleepRecordService:
    
    @staticmethod
    def create_sleep_record(db: Session, sleep_record: SleepRecordCreate) -> SleepRecord:
        """创建睡眠记录"""
        db_sleep_record = SleepRecord(
            user_id=sleep_record.user_id,
            sleep_date=sleep_record.sleep_date,
            bedtime=sleep_record.bedtime,
            wake_time=sleep_record.wake_time,
            sleep_duration=sleep_record.sleep_duration,
            sleep_quality=sleep_record.sleep_quality,
            deep_sleep_hours=sleep_record.deep_sleep_hours,
            notes=sleep_record.notes,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(db_sleep_record)
        db.commit()
        db.refresh(db_sleep_record)
        return db_sleep_record
    
    @staticmethod
    def get_sleep_records_by_user(
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[SleepRecord]:
        """获取用户的睡眠记录"""
        return db.query(SleepRecord).filter(
            SleepRecord.user_id == user_id
        ).order_by(SleepRecord.sleep_date.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_sleep_record_by_id(db: Session, sleep_id: int) -> Optional[SleepRecord]:
        """根据ID获取睡眠记录"""
        return db.query(SleepRecord).filter(SleepRecord.sleep_id == sleep_id).first()
    
    @staticmethod
    def delete_sleep_record(db: Session, sleep_id: int) -> bool:
        """删除睡眠记录"""
        db_sleep_record = db.query(SleepRecord).filter(SleepRecord.sleep_id == sleep_id).first()
        if db_sleep_record:
            db.delete(db_sleep_record)
            db.commit()
            return True
        return False 