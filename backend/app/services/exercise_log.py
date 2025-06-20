from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from app.models.exercise_log import ExerciseLog
from app.schemas.exercise_log import ExerciseLogCreate

class ExerciseLogService:
    
    @staticmethod
    def create_exercise_log(db: Session, exercise_log: ExerciseLogCreate) -> ExerciseLog:
        """创建运动记录"""
        db_exercise_log = ExerciseLog(
            user_id=exercise_log.user_id,
            exercise_type=exercise_log.exercise_type,
            duration_minutes=exercise_log.duration_minutes,
            log_date=exercise_log.log_date,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(db_exercise_log)
        db.commit()
        db.refresh(db_exercise_log)
        return db_exercise_log
    
    @staticmethod
    def get_exercise_logs_by_user(
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ExerciseLog]:
        """获取用户的运动记录"""
        return db.query(ExerciseLog).filter(
            ExerciseLog.user_id == user_id
        ).order_by(ExerciseLog.log_date.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_exercise_log_by_id(db: Session, log_id: int) -> Optional[ExerciseLog]:
        """根据ID获取运动记录"""
        return db.query(ExerciseLog).filter(ExerciseLog.log_id == log_id).first()
    
    @staticmethod
    def delete_exercise_log(db: Session, log_id: int) -> bool:
        """删除运动记录"""
        db_exercise_log = db.query(ExerciseLog).filter(ExerciseLog.log_id == log_id).first()
        if db_exercise_log:
            db.delete(db_exercise_log)
            db.commit()
            return True
        return False 