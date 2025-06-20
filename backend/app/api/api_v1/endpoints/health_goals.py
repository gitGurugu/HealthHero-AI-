from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.health_goals import HealthGoalsCreate, HealthGoalsResponse
from app.db.session import get_db
from app.services.health_goals import HealthGoalsService

router = APIRouter()

@router.post("/", response_model=HealthGoalsResponse, status_code=status.HTTP_201_CREATED)
def create_health_goal(
    health_goal: HealthGoalsCreate,
    db: Session = Depends(get_db)
):
    """
    创建健康目标
    
    - **user_id**: 用户ID
    - **goal_type**: 目标类型
    - **title**: 目标标题
    - **description**: 目标描述
    - **target_value**: 目标值
    - **current_value**: 当前值
    - **unit**: 单位
    - **start_date**: 开始日期
    - **target_date**: 目标日期
    - **status**: 状态
    """
    try:
        return HealthGoalsService.create_health_goal(db=db, health_goal=health_goal)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建健康目标失败: {str(e)}"
        )

@router.get("/user/{user_id}", response_model=List[HealthGoalsResponse])
def get_user_health_goals(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取用户的健康目标"""
    try:
        return HealthGoalsService.get_health_goals_by_user(
            db=db, user_id=user_id, skip=skip, limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取健康目标失败: {str(e)}"
        )

@router.get("/{goal_id}", response_model=HealthGoalsResponse)
def get_health_goal(
    goal_id: int,
    db: Session = Depends(get_db)
):
    """根据ID获取健康目标"""
    health_goal = HealthGoalsService.get_health_goal_by_id(db=db, goal_id=goal_id)
    if not health_goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="健康目标未找到"
        )
    return health_goal

@router.put("/{goal_id}", response_model=HealthGoalsResponse)
def update_health_goal(
    goal_id: int,
    health_goal_update: HealthGoalsCreate,
    db: Session = Depends(get_db)
):
    """更新健康目标"""
    health_goal = HealthGoalsService.update_health_goal(
        db=db, goal_id=goal_id, health_goal_update=health_goal_update
    )
    if not health_goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="健康目标未找到"
        )
    return health_goal

@router.delete("/{goal_id}")
def delete_health_goal(
    goal_id: int,
    db: Session = Depends(get_db)
):
    """删除健康目标"""
    success = HealthGoalsService.delete_health_goal(db=db, goal_id=goal_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="健康目标未找到"
        )
    return {"message": "健康目标已成功删除"} 