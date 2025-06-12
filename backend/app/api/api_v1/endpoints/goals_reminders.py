from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import List, Optional
from datetime import date, datetime, time
from app.db.session import get_db
from app.models import HealthGoal, HealthReminder, GoalStatus, GoalType, ReminderType, ReminderFrequency
from pydantic import BaseModel

router = APIRouter()

# 目标相关的Pydantic模型
class HealthGoalCreate(BaseModel):
    goal_type: GoalType
    title: str
    description: Optional[str] = None
    target_value: float
    current_value: Optional[float] = 0
    unit: Optional[str] = None
    start_date: date
    target_date: date

class HealthGoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    unit: Optional[str] = None
    target_date: Optional[date] = None
    status: Optional[GoalStatus] = None

class HealthGoalResponse(BaseModel):
    goal_id: int
    user_id: int
    goal_type: GoalType
    title: str
    description: Optional[str]
    target_value: float
    current_value: Optional[float]
    unit: Optional[str]
    start_date: date
    target_date: date
    status: GoalStatus
    progress_percentage: float
    days_remaining: int
    created_at: datetime

    class Config:
        from_attributes = True

# 提醒相关的Pydantic模型
class HealthReminderCreate(BaseModel):
    reminder_type: ReminderType
    title: str
    description: Optional[str] = None
    reminder_time: time
    frequency: ReminderFrequency
    days_of_week: Optional[str] = None
    custom_interval_days: Optional[int] = None

class HealthReminderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    reminder_time: Optional[time] = None
    frequency: Optional[ReminderFrequency] = None
    days_of_week: Optional[str] = None
    is_active: Optional[bool] = None
    custom_interval_days: Optional[int] = None

class HealthReminderResponse(BaseModel):
    reminder_id: int
    user_id: int
    reminder_type: ReminderType
    title: str
    description: Optional[str]
    reminder_time: time
    frequency: ReminderFrequency
    days_of_week: Optional[str]
    is_active: bool
    custom_interval_days: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

# ===== 健康目标相关端点 =====

@router.get("/goals/{user_id}", response_model=List[HealthGoalResponse])
async def get_user_goals(
    user_id: int,
    status: Optional[GoalStatus] = None,
    db: Session = Depends(get_db)
):
    """获取用户的健康目标列表"""
    
    query = db.query(HealthGoal).filter(HealthGoal.user_id == user_id)
    
    if status:
        query = query.filter(HealthGoal.status == status)
    
    goals = query.order_by(desc(HealthGoal.created_at)).all()
    
    # 计算进度和剩余天数
    result = []
    today = date.today()
    
    for goal in goals:
        # 计算进度百分比
        if goal.target_value > 0:
            progress = (goal.current_value or 0) / goal.target_value * 100
            progress = min(100, max(0, progress))  # 限制在0-100之间
        else:
            progress = 0
        
        # 计算剩余天数
        days_remaining = (goal.target_date - today).days
        
        goal_data = HealthGoalResponse(
            goal_id=goal.goal_id,
            user_id=goal.user_id,
            goal_type=goal.goal_type,
            title=goal.title,
            description=goal.description,
            target_value=goal.target_value,
            current_value=goal.current_value,
            unit=goal.unit,
            start_date=goal.start_date,
            target_date=goal.target_date,
            status=goal.status,
            progress_percentage=round(progress, 1),
            days_remaining=days_remaining,
            created_at=goal.created_at
        )
        result.append(goal_data)
    
    return result

@router.post("/goals/{user_id}", response_model=HealthGoalResponse)
async def create_health_goal(
    user_id: int,
    goal_data: HealthGoalCreate,
    db: Session = Depends(get_db)
):
    """创建新的健康目标"""
    
    new_goal = HealthGoal(
        user_id=user_id,
        goal_type=goal_data.goal_type,
        title=goal_data.title,
        description=goal_data.description,
        target_value=goal_data.target_value,
        current_value=goal_data.current_value,
        unit=goal_data.unit,
        start_date=goal_data.start_date,
        target_date=goal_data.target_date,
        status=GoalStatus.ACTIVE,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    
    # 计算进度和剩余天数
    progress = (new_goal.current_value or 0) / new_goal.target_value * 100 if new_goal.target_value > 0 else 0
    days_remaining = (new_goal.target_date - date.today()).days
    
    return HealthGoalResponse(
        goal_id=new_goal.goal_id,
        user_id=new_goal.user_id,
        goal_type=new_goal.goal_type,
        title=new_goal.title,
        description=new_goal.description,
        target_value=new_goal.target_value,
        current_value=new_goal.current_value,
        unit=new_goal.unit,
        start_date=new_goal.start_date,
        target_date=new_goal.target_date,
        status=new_goal.status,
        progress_percentage=round(progress, 1),
        days_remaining=days_remaining,
        created_at=new_goal.created_at
    )

@router.put("/goals/{goal_id}", response_model=HealthGoalResponse)
async def update_health_goal(
    goal_id: int,
    goal_update: HealthGoalUpdate,
    db: Session = Depends(get_db)
):
    """更新健康目标"""
    
    goal = db.query(HealthGoal).filter(HealthGoal.goal_id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="目标不存在")
    
    # 更新字段
    update_data = goal_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(goal, field, value)
    
    goal.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(goal)
    
    # 计算进度和剩余天数
    progress = (goal.current_value or 0) / goal.target_value * 100 if goal.target_value > 0 else 0
    days_remaining = (goal.target_date - date.today()).days
    
    return HealthGoalResponse(
        goal_id=goal.goal_id,
        user_id=goal.user_id,
        goal_type=goal.goal_type,
        title=goal.title,
        description=goal.description,
        target_value=goal.target_value,
        current_value=goal.current_value,
        unit=goal.unit,
        start_date=goal.start_date,
        target_date=goal.target_date,
        status=goal.status,
        progress_percentage=round(progress, 1),
        days_remaining=days_remaining,
        created_at=goal.created_at
    )

@router.delete("/goals/{goal_id}")
async def delete_health_goal(
    goal_id: int,
    db: Session = Depends(get_db)
):
    """删除健康目标"""
    
    goal = db.query(HealthGoal).filter(HealthGoal.goal_id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="目标不存在")
    
    db.delete(goal)
    db.commit()
    
    return {"message": "目标已删除"}

# ===== 健康提醒相关端点 =====

@router.get("/reminders/{user_id}", response_model=List[HealthReminderResponse])
async def get_user_reminders(
    user_id: int,
    is_active: Optional[bool] = None,
    reminder_type: Optional[ReminderType] = None,
    db: Session = Depends(get_db)
):
    """获取用户的健康提醒列表"""
    
    query = db.query(HealthReminder).filter(HealthReminder.user_id == user_id)
    
    if is_active is not None:
        query = query.filter(HealthReminder.is_active == is_active)
    
    if reminder_type:
        query = query.filter(HealthReminder.reminder_type == reminder_type)
    
    reminders = query.order_by(HealthReminder.reminder_time).all()
    
    return [HealthReminderResponse(
        reminder_id=reminder.reminder_id,
        user_id=reminder.user_id,
        reminder_type=reminder.reminder_type,
        title=reminder.title,
        description=reminder.description,
        reminder_time=reminder.reminder_time,
        frequency=reminder.frequency,
        days_of_week=reminder.days_of_week,
        is_active=reminder.is_active,
        custom_interval_days=reminder.custom_interval_days,
        created_at=reminder.created_at
    ) for reminder in reminders]

@router.post("/reminders/{user_id}", response_model=HealthReminderResponse)
async def create_health_reminder(
    user_id: int,
    reminder_data: HealthReminderCreate,
    db: Session = Depends(get_db)
):
    """创建新的健康提醒"""
    
    new_reminder = HealthReminder(
        user_id=user_id,
        reminder_type=reminder_data.reminder_type,
        title=reminder_data.title,
        description=reminder_data.description,
        reminder_time=reminder_data.reminder_time,
        frequency=reminder_data.frequency,
        days_of_week=reminder_data.days_of_week,
        is_active=True,
        custom_interval_days=reminder_data.custom_interval_days,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_reminder)
    db.commit()
    db.refresh(new_reminder)
    
    return HealthReminderResponse(
        reminder_id=new_reminder.reminder_id,
        user_id=new_reminder.user_id,
        reminder_type=new_reminder.reminder_type,
        title=new_reminder.title,
        description=new_reminder.description,
        reminder_time=new_reminder.reminder_time,
        frequency=new_reminder.frequency,
        days_of_week=new_reminder.days_of_week,
        is_active=new_reminder.is_active,
        custom_interval_days=new_reminder.custom_interval_days,
        created_at=new_reminder.created_at
    )

@router.put("/reminders/{reminder_id}", response_model=HealthReminderResponse)
async def update_health_reminder(
    reminder_id: int,
    reminder_update: HealthReminderUpdate,
    db: Session = Depends(get_db)
):
    """更新健康提醒"""
    
    reminder = db.query(HealthReminder).filter(HealthReminder.reminder_id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="提醒不存在")
    
    # 更新字段
    update_data = reminder_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(reminder, field, value)
    
    reminder.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(reminder)
    
    return HealthReminderResponse(
        reminder_id=reminder.reminder_id,
        user_id=reminder.user_id,
        reminder_type=reminder.reminder_type,
        title=reminder.title,
        description=reminder.description,
        reminder_time=reminder.reminder_time,
        frequency=reminder.frequency,
        days_of_week=reminder.days_of_week,
        is_active=reminder.is_active,
        custom_interval_days=reminder.custom_interval_days,
        created_at=reminder.created_at
    )

@router.delete("/reminders/{reminder_id}")
async def delete_health_reminder(
    reminder_id: int,
    db: Session = Depends(get_db)
):
    """删除健康提醒"""
    
    reminder = db.query(HealthReminder).filter(HealthReminder.reminder_id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="提醒不存在")
    
    db.delete(reminder)
    db.commit()
    
    return {"message": "提醒已删除"}

@router.get("/goals/progress/{user_id}")
async def get_goals_progress_summary(
    user_id: int,
    db: Session = Depends(get_db)
):
    """获取用户目标进度汇总"""
    
    goals = db.query(HealthGoal).filter(
        and_(HealthGoal.user_id == user_id, HealthGoal.status == GoalStatus.ACTIVE)
    ).all()
    
    progress_summary = []
    for goal in goals:
        progress = (goal.current_value or 0) / goal.target_value * 100 if goal.target_value > 0 else 0
        progress_summary.append({
            "goal_id": goal.goal_id,
            "title": goal.title,
            "goal_type": goal.goal_type.value,
            "progress_percentage": round(progress, 1),
            "current_value": goal.current_value,
            "target_value": goal.target_value,
            "unit": goal.unit,
            "target_date": goal.target_date.isoformat(),
            "days_remaining": (goal.target_date - date.today()).days
        })
    
    return {
        "total_active_goals": len(goals),
        "goals_progress": progress_summary
    } 