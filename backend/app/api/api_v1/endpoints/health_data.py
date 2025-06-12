from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import date, datetime, timedelta
from app.db.session import get_db
from app.models import (
    HealthData, DietRecord, ExerciseLog, SleepRecord, 
    HealthGoal, SymptomRecord, BodyMeasurement, HealthReminder,
    User
)
from pydantic import BaseModel

router = APIRouter()

# Pydantic 模型定义
class HealthDataResponse(BaseModel):
    record_id: int
    user_id: int
    record_date: date
    height: Optional[float]
    weight: Optional[float]
    systolic_pressure: Optional[int]
    diastolic_pressure: Optional[int]
    blood_sugar: Optional[float]
    cholesterol: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True

class HealthDashboardResponse(BaseModel):
    latest_health_data: Optional[HealthDataResponse]
    weight_trend: List[dict]
    blood_pressure_trend: List[dict]
    active_goals_count: int
    completed_goals_count: int
    recent_symptoms: List[dict]
    sleep_quality_avg: Optional[float]
    exercise_minutes_week: int

# 获取用户健康仪表板数据
@router.get("/dashboard/{user_id}", response_model=HealthDashboardResponse)
async def get_health_dashboard(
    user_id: int,
    db: Session = Depends(get_db)
):
    """获取用户健康仪表板概览数据"""
    
    # 获取最新健康数据
    latest_health = db.query(HealthData).filter(
        HealthData.user_id == user_id
    ).order_by(desc(HealthData.record_date)).first()
    
    # 获取近30天体重趋势
    thirty_days_ago = date.today() - timedelta(days=30)
    weight_trend = db.query(
        HealthData.record_date,
        HealthData.weight
    ).filter(
        HealthData.user_id == user_id,
        HealthData.record_date >= thirty_days_ago,
        HealthData.weight.isnot(None)
    ).order_by(HealthData.record_date).all()
    
    weight_trend_data = [
        {"date": item.record_date.isoformat(), "weight": float(item.weight)}
        for item in weight_trend
    ]
    
    # 获取血压趋势
    bp_trend = db.query(
        HealthData.record_date,
        HealthData.systolic_pressure,
        HealthData.diastolic_pressure
    ).filter(
        HealthData.user_id == user_id,
        HealthData.record_date >= thirty_days_ago,
        HealthData.systolic_pressure.isnot(None)
    ).order_by(HealthData.record_date).all()
    
    bp_trend_data = [
        {
            "date": item.record_date.isoformat(),
            "systolic": item.systolic_pressure,
            "diastolic": item.diastolic_pressure
        }
        for item in bp_trend
    ]
    
    # 获取目标统计
    active_goals = db.query(func.count(HealthGoal.goal_id)).filter(
        HealthGoal.user_id == user_id,
        HealthGoal.status == 'ACTIVE'
    ).scalar()
    
    completed_goals = db.query(func.count(HealthGoal.goal_id)).filter(
        HealthGoal.user_id == user_id,
        HealthGoal.status == 'COMPLETED'
    ).scalar()
    
    # 获取最近症状记录
    recent_symptoms = db.query(SymptomRecord).filter(
        SymptomRecord.user_id == user_id,
        SymptomRecord.record_date >= thirty_days_ago
    ).order_by(desc(SymptomRecord.record_date)).limit(5).all()
    
    symptoms_data = [
        {
            "date": symptom.record_date.isoformat(),
            "type": symptom.symptom_type,
            "severity": symptom.severity
        }
        for symptom in recent_symptoms
    ]
    
    # 获取平均睡眠质量
    sleep_quality_avg = db.query(func.avg(SleepRecord.sleep_quality)).filter(
        SleepRecord.user_id == user_id,
        SleepRecord.sleep_date >= thirty_days_ago,
        SleepRecord.sleep_quality.isnot(None)
    ).scalar()
    
    # 获取本周运动时长
    week_start = date.today() - timedelta(days=date.today().weekday())
    exercise_minutes = db.query(func.sum(ExerciseLog.duration_minutes)).filter(
        ExerciseLog.user_id == user_id,
        ExerciseLog.log_date >= week_start
    ).scalar() or 0
    
    return HealthDashboardResponse(
        latest_health_data=latest_health,
        weight_trend=weight_trend_data,
        blood_pressure_trend=bp_trend_data,
        active_goals_count=active_goals or 0,
        completed_goals_count=completed_goals or 0,
        recent_symptoms=symptoms_data,
        sleep_quality_avg=float(sleep_quality_avg) if sleep_quality_avg else None,
        exercise_minutes_week=exercise_minutes
    )

# 获取健康数据列表
@router.get("/health-data/{user_id}")
async def get_health_data_list(
    user_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """获取用户健康数据列表"""
    
    query = db.query(HealthData).filter(HealthData.user_id == user_id)
    
    if start_date:
        query = query.filter(HealthData.record_date >= start_date)
    if end_date:
        query = query.filter(HealthData.record_date <= end_date)
    
    total = query.count()
    data = query.order_by(desc(HealthData.record_date)).offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "data": data,
        "limit": limit,
        "offset": offset
    }

# 获取饮食记录
@router.get("/diet-records/{user_id}")
async def get_diet_records(
    user_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """获取用户饮食记录"""
    
    query = db.query(DietRecord).filter(DietRecord.user_id == user_id)
    
    if start_date:
        query = query.filter(DietRecord.record_date >= start_date)
    if end_date:
        query = query.filter(DietRecord.record_date <= end_date)
    
    total = query.count()
    data = query.order_by(desc(DietRecord.record_date)).offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "data": data,
        "limit": limit,
        "offset": offset
    }

# 获取运动日志
@router.get("/exercise-logs/{user_id}")
async def get_exercise_logs(
    user_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """获取用户运动日志"""
    
    query = db.query(ExerciseLog).filter(ExerciseLog.user_id == user_id)
    
    if start_date:
        query = query.filter(ExerciseLog.log_date >= start_date)
    if end_date:
        query = query.filter(ExerciseLog.log_date <= end_date)
    
    total = query.count()
    data = query.order_by(desc(ExerciseLog.log_date)).offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "data": data,
        "limit": limit,
        "offset": offset
    }

# 获取睡眠记录
@router.get("/sleep-records/{user_id}")
async def get_sleep_records(
    user_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """获取用户睡眠记录"""
    
    query = db.query(SleepRecord).filter(SleepRecord.user_id == user_id)
    
    if start_date:
        query = query.filter(SleepRecord.sleep_date >= start_date)
    if end_date:
        query = query.filter(SleepRecord.sleep_date <= end_date)
    
    total = query.count()
    data = query.order_by(desc(SleepRecord.sleep_date)).offset(offset).limit(limit).all()
    
    # 计算睡眠统计
    avg_duration = db.query(func.avg(SleepRecord.sleep_duration)).filter(
        SleepRecord.user_id == user_id,
        SleepRecord.sleep_duration.isnot(None)
    ).scalar()
    
    avg_quality = db.query(func.avg(SleepRecord.sleep_quality)).filter(
        SleepRecord.user_id == user_id,
        SleepRecord.sleep_quality.isnot(None)
    ).scalar()
    
    return {
        "total": total,
        "data": data,
        "limit": limit,
        "offset": offset,
        "statistics": {
            "average_duration": float(avg_duration) if avg_duration else None,
            "average_quality": float(avg_quality) if avg_quality else None
        }
    }

# 获取健康统计数据
@router.get("/statistics/{user_id}")
async def get_health_statistics(
    user_id: int,
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db)
):
    """获取用户健康统计数据"""
    
    start_date = date.today() - timedelta(days=days)
    
    # 体重统计
    weight_stats = db.query(
        func.min(HealthData.weight).label('min_weight'),
        func.max(HealthData.weight).label('max_weight'),
        func.avg(HealthData.weight).label('avg_weight')
    ).filter(
        HealthData.user_id == user_id,
        HealthData.record_date >= start_date,
        HealthData.weight.isnot(None)
    ).first()
    
    # 血压统计
    bp_stats = db.query(
        func.min(HealthData.systolic_pressure).label('min_systolic'),
        func.max(HealthData.systolic_pressure).label('max_systolic'),
        func.avg(HealthData.systolic_pressure).label('avg_systolic'),
        func.min(HealthData.diastolic_pressure).label('min_diastolic'),
        func.max(HealthData.diastolic_pressure).label('max_diastolic'),
        func.avg(HealthData.diastolic_pressure).label('avg_diastolic')
    ).filter(
        HealthData.user_id == user_id,
        HealthData.record_date >= start_date,
        HealthData.systolic_pressure.isnot(None)
    ).first()
    
    # 运动统计
    exercise_stats = db.query(
        func.sum(ExerciseLog.duration_minutes).label('total_minutes'),
        func.count(ExerciseLog.log_id).label('total_sessions')
    ).filter(
        ExerciseLog.user_id == user_id,
        ExerciseLog.log_date >= start_date
    ).first()
    
    return {
        "period_days": days,
        "weight_statistics": {
            "min": float(weight_stats.min_weight) if weight_stats.min_weight else None,
            "max": float(weight_stats.max_weight) if weight_stats.max_weight else None,
            "average": float(weight_stats.avg_weight) if weight_stats.avg_weight else None
        },
        "blood_pressure_statistics": {
            "systolic": {
                "min": bp_stats.min_systolic if bp_stats.min_systolic else None,
                "max": bp_stats.max_systolic if bp_stats.max_systolic else None,
                "average": float(bp_stats.avg_systolic) if bp_stats.avg_systolic else None
            },
            "diastolic": {
                "min": bp_stats.min_diastolic if bp_stats.min_diastolic else None,
                "max": bp_stats.max_diastolic if bp_stats.max_diastolic else None,
                "average": float(bp_stats.avg_diastolic) if bp_stats.avg_diastolic else None
            }
        },
        "exercise_statistics": {
            "total_minutes": exercise_stats.total_minutes or 0,
            "total_sessions": exercise_stats.total_sessions or 0,
            "average_per_session": (
                exercise_stats.total_minutes / exercise_stats.total_sessions 
                if exercise_stats.total_sessions and exercise_stats.total_minutes 
                else 0
            )
        }
    } 