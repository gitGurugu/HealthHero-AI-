from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from app.models.health_goals import HealthGoal
from app.schemas.health_goals import HealthGoalsCreate

class HealthGoalsService:
    
    @staticmethod
    def create_health_goal(db: Session, health_goal: HealthGoalsCreate) -> HealthGoal:
        """创建健康目标"""
        db_health_goal = HealthGoal(
            user_id=health_goal.user_id,
            goal_type=health_goal.goal_type,
            title=health_goal.title,
            description=health_goal.description,
            target_value=health_goal.target_value,
            current_value=health_goal.current_value,
            unit=health_goal.unit,
            start_date=health_goal.start_date,
            target_date=health_goal.target_date,
            status=health_goal.status,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(db_health_goal)
        db.commit()
        db.refresh(db_health_goal)
        return db_health_goal
    
    @staticmethod
    def get_health_goals_by_user(
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[HealthGoal]:
        """获取用户的健康目标"""
        return db.query(HealthGoal).filter(
            HealthGoal.user_id == user_id
        ).order_by(HealthGoal.target_date.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_health_goal_by_id(db: Session, goal_id: int) -> Optional[HealthGoal]:
        """根据ID获取健康目标"""
        return db.query(HealthGoal).filter(HealthGoal.goal_id == goal_id).first()
    
    @staticmethod
    def update_health_goal(
        db: Session, 
        goal_id: int, 
        health_goal_update: HealthGoalsCreate
    ) -> Optional[HealthGoal]:
        """更新健康目标"""
        db_health_goal = db.query(HealthGoal).filter(HealthGoal.goal_id == goal_id).first()
        if db_health_goal:
            for field, value in health_goal_update.dict(exclude_unset=True).items():
                setattr(db_health_goal, field, value)
            db_health_goal.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_health_goal)
        return db_health_goal
    
    @staticmethod
    def delete_health_goal(db: Session, goal_id: int) -> bool:
        """删除健康目标"""
        db_health_goal = db.query(HealthGoal).filter(HealthGoal.goal_id == goal_id).first()
        if db_health_goal:
            db.delete(db_health_goal)
            db.commit()
            return True
        return False 