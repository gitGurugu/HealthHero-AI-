from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc, Date
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import logging

from app.db.session import get_db
from app.models.health_data import HealthData
from app.models.user import User
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()

class HealthStatsResponse(BaseModel):
    total_records: int
    total_users: int
    avg_bmi: Optional[float]
    avg_systolic: Optional[float]
    avg_diastolic: Optional[float]
    avg_blood_sugar: Optional[float]
    avg_cholesterol: Optional[float]

class TrendDataPoint(BaseModel):
    date: str
    value: Optional[float]
    count: int

class HealthTrendResponse(BaseModel):
    metric: str
    data: List[TrendDataPoint]
    period: str

class UserHealthSummary(BaseModel):
    user_id: int
    username: str
    latest_record_date: Optional[datetime]
    bmi: Optional[float]
    health_score: Optional[float]
    risk_level: str

class HealthDistribution(BaseModel):
    category: str
    count: int
    percentage: float

@router.get("/overview", response_model=HealthStatsResponse)
def get_health_overview(
    user_id: Optional[int] = Query(None, description="特定用户ID，不提供则返回全局统计"),
    db: Session = Depends(get_db)
):
    """
    获取健康数据概览统计
    """
    try:
        query = db.query(HealthData)
        if user_id:
            query = query.filter(HealthData.user_id == user_id)
        
        # 基础统计
        total_records = query.count()
        total_users = db.query(HealthData.user_id).distinct().count() if not user_id else 1
        
        # 计算平均值（排除空值）
        stats = query.filter(
            HealthData.height.isnot(None),
            HealthData.weight.isnot(None)
        ).with_entities(
            func.avg(HealthData.weight / func.power(HealthData.height / 100, 2)).label('avg_bmi'),
            func.avg(HealthData.systolic_pressure).label('avg_systolic'),
            func.avg(HealthData.diastolic_pressure).label('avg_diastolic'),
            func.avg(HealthData.blood_sugar).label('avg_blood_sugar'),
            func.avg(HealthData.cholesterol).label('avg_cholesterol')
        ).first()
        
        return HealthStatsResponse(
            total_records=total_records,
            total_users=total_users,
            avg_bmi=float(stats.avg_bmi) if stats.avg_bmi else None,
            avg_systolic=float(stats.avg_systolic) if stats.avg_systolic else None,
            avg_diastolic=float(stats.avg_diastolic) if stats.avg_diastolic else None,
            avg_blood_sugar=float(stats.avg_blood_sugar) if stats.avg_blood_sugar else None,
            avg_cholesterol=float(stats.avg_cholesterol) if stats.avg_cholesterol else None
        )
        
    except Exception as e:
        logger.error(f"获取健康概览失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取健康概览失败: {str(e)}"
        )

@router.get("/trends/{metric}", response_model=HealthTrendResponse)
def get_health_trends(
    metric: str,
    user_id: Optional[int] = Query(None, description="特定用户ID"),
    period: str = Query("30d", description="时间周期: 7d, 30d, 90d, 1y"),
    db: Session = Depends(get_db)
):
    """
    获取健康指标趋势数据
    支持的指标: weight, bmi, systolic, diastolic, blood_sugar, cholesterol
    """
    try:
        # 计算时间范围
        period_days = {
            "7d": 7,
            "30d": 30,
            "90d": 90,
            "1y": 365
        }
        
        if period not in period_days:
            raise HTTPException(status_code=400, detail="无效的时间周期")
        
        start_date = datetime.now() - timedelta(days=period_days[period])
        
        query = db.query(HealthData).filter(
            HealthData.record_date >= start_date
        )
        
        if user_id:
            query = query.filter(HealthData.user_id == user_id)
        
        # 根据指标选择字段
        metric_fields = {
            "weight": HealthData.weight,
            "bmi": HealthData.weight / func.power(HealthData.height / 100, 2),
            "systolic": HealthData.systolic_pressure,
            "diastolic": HealthData.diastolic_pressure,
            "blood_sugar": HealthData.blood_sugar,
            "cholesterol": HealthData.cholesterol
        }
        
        if metric not in metric_fields:
            raise HTTPException(status_code=400, detail="无效的健康指标")
        
        field = metric_fields[metric]
        
        # 按日期分组统计
        results = query.filter(field.isnot(None)).with_entities(
            HealthData.record_date.cast(Date).label('date'),
            func.avg(field).label('avg_value'),
            func.count().label('count')
        ).group_by(
            HealthData.record_date.cast(Date)
        ).order_by(asc('date')).all()
        
        trend_data = [
            TrendDataPoint(
                date=result.date.strftime('%Y-%m-%d'),
                value=float(result.avg_value) if result.avg_value else None,
                count=result.count
            )
            for result in results
        ]
        
        return HealthTrendResponse(
            metric=metric,
            data=trend_data,
            period=period
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取健康趋势失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取健康趋势失败: {str(e)}"
        )

@router.get("/users/summary", response_model=List[UserHealthSummary])
def get_users_health_summary(
    limit: int = Query(10, description="返回用户数量限制"),
    user_id: Optional[int] = Query(None, description="特定用户ID"),
    db: Session = Depends(get_db)
):
    """
    获取用户健康状况摘要
    """
    try:
        # 获取每个用户的最新健康记录
        subquery = db.query(
            HealthData.user_id,
            func.max(HealthData.record_date).label('latest_date')
        ).group_by(HealthData.user_id)
        
        # 如果指定了用户ID，只查询该用户
        if user_id:
            subquery = subquery.filter(HealthData.user_id == user_id)
        
        subquery = subquery.subquery()
        
        results = db.query(
            HealthData,
            User.username
        ).join(
            User, HealthData.user_id == User.id
        ).join(
            subquery,
            (HealthData.user_id == subquery.c.user_id) &
            (HealthData.record_date == subquery.c.latest_date)
        ).limit(limit).all()
        
        summaries = []
        for health_data, username in results:
            # 计算BMI
            bmi = None
            if health_data.height and health_data.weight:
                bmi = float(health_data.weight) / (float(health_data.height) / 100) ** 2
            
            # 计算健康评分（简化版）
            health_score = None
            risk_level = "未知"
            
            if bmi:
                if bmi < 18.5:
                    health_score = 70.0
                    risk_level = "偏瘦"
                elif 18.5 <= bmi < 24:
                    health_score = 90.0
                    risk_level = "正常"
                elif 24 <= bmi < 28:
                    health_score = 75.0
                    risk_level = "超重"
                else:
                    health_score = 60.0
                    risk_level = "肥胖"
                
                # 根据血压调整评分
                if health_data.systolic_pressure and health_data.diastolic_pressure:
                    if health_data.systolic_pressure > 140 or health_data.diastolic_pressure > 90:
                        health_score -= 15
                        risk_level = "高风险"
                    elif health_data.systolic_pressure > 130 or health_data.diastolic_pressure > 85:
                        health_score -= 10
            
            summaries.append(UserHealthSummary(
                user_id=health_data.user_id,
                username=username,
                latest_record_date=health_data.record_date,
                bmi=bmi,
                health_score=health_score,
                risk_level=risk_level
            ))
        
        return summaries
        
    except Exception as e:
        logger.error(f"获取用户健康摘要失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户健康摘要失败: {str(e)}"
        )

@router.get("/distribution/{metric}", response_model=List[HealthDistribution])
def get_health_distribution(
    metric: str,
    user_id: Optional[int] = Query(None, description="特定用户ID"),
    db: Session = Depends(get_db)
):
    """
    获取健康指标分布统计
    支持的指标: bmi_category, blood_pressure_category, blood_sugar_category
    """
    try:
        query = db.query(HealthData)
        if user_id:
            query = query.filter(HealthData.user_id == user_id)
        
        if metric == "bmi_category":
            # BMI分类统计
            records = query.filter(
                HealthData.height.isnot(None),
                HealthData.weight.isnot(None)
            ).all()
            
            categories = {"偏瘦": 0, "正常": 0, "超重": 0, "肥胖": 0}
            
            for record in records:
                bmi = float(record.weight) / (float(record.height) / 100) ** 2
                if bmi < 18.5:
                    categories["偏瘦"] += 1
                elif bmi < 24:
                    categories["正常"] += 1
                elif bmi < 28:
                    categories["超重"] += 1
                else:
                    categories["肥胖"] += 1
            
        elif metric == "blood_pressure_category":
            # 血压分类统计
            records = query.filter(
                HealthData.systolic_pressure.isnot(None),
                HealthData.diastolic_pressure.isnot(None)
            ).all()
            
            categories = {"正常": 0, "偏高": 0, "高血压": 0}
            
            for record in records:
                if record.systolic_pressure < 120 and record.diastolic_pressure < 80:
                    categories["正常"] += 1
                elif record.systolic_pressure < 140 and record.diastolic_pressure < 90:
                    categories["偏高"] += 1
                else:
                    categories["高血压"] += 1
                    
        elif metric == "blood_sugar_category":
            # 血糖分类统计
            records = query.filter(HealthData.blood_sugar.isnot(None)).all()
            
            categories = {"正常": 0, "偏高": 0, "糖尿病": 0}
            
            for record in records:
                blood_sugar = float(record.blood_sugar)
                if blood_sugar < 6.1:
                    categories["正常"] += 1
                elif blood_sugar < 7.0:
                    categories["偏高"] += 1
                else:
                    categories["糖尿病"] += 1
        else:
            raise HTTPException(status_code=400, detail="无效的分布指标")
        
        total = sum(categories.values())
        if total == 0:
            return []
        
        distribution = [
            HealthDistribution(
                category=category,
                count=count,
                percentage=round(count / total * 100, 1)
            )
            for category, count in categories.items()
            if count > 0
        ]
        
        return distribution
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取健康分布统计失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取健康分布统计失败: {str(e)}"
        )