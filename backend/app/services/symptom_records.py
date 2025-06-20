from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from app.models.symptom_records import SymptomRecord
from app.schemas.symptom_records import SymptomRecordsCreate

class SymptomRecordsService:
    
    @staticmethod
    def create_symptom_record(db: Session, symptom_record: SymptomRecordsCreate) -> SymptomRecord:
        """创建症状记录"""
        db_symptom_record = SymptomRecord(
            user_id=symptom_record.user_id,
            record_date=symptom_record.record_date,
            symptom_type=symptom_record.symptom_type,
            severity=symptom_record.severity,
            description=symptom_record.description,
            duration_hours=symptom_record.duration_hours,
            location=symptom_record.location,
            triggers=symptom_record.triggers,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(db_symptom_record)
        db.commit()
        db.refresh(db_symptom_record)
        return db_symptom_record
    
    @staticmethod
    def get_symptom_records_by_user(
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[SymptomRecord]:
        """获取用户的症状记录"""
        return db.query(SymptomRecord).filter(
            SymptomRecord.user_id == user_id
        ).order_by(SymptomRecord.record_date.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_symptom_record_by_id(db: Session, symptom_id: int) -> Optional[SymptomRecord]:
        """根据ID获取症状记录"""
        return db.query(SymptomRecord).filter(SymptomRecord.symptom_id == symptom_id).first()
    
    @staticmethod
    def delete_symptom_record(db: Session, symptom_id: int) -> bool:
        """删除症状记录"""
        db_symptom_record = db.query(SymptomRecord).filter(SymptomRecord.symptom_id == symptom_id).first()
        if db_symptom_record:
            db.delete(db_symptom_record)
            db.commit()
            return True
        return False 