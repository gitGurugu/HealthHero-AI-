from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.exercise_log import ExerciseLogCreate, ExerciseLogResponse
from app.db.session import get_db
from app.services.exercise_log import ExerciseLogService

router = APIRouter()

@router.get("/", response_model=List[ExerciseLogResponse])
def get_exercise_logs_list(
    skip: int = 0,
    limit: int = 10,
    user_id: int = None,
    db: Session = Depends(get_db)
):
    """
    获取运动记录列表
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的记录数限制
    - **user_id**: 可选，指定用户ID
    """
    try:
        if user_id:
            return ExerciseLogService.get_exercise_logs_by_user(
                db=db, user_id=user_id, skip=skip, limit=limit
            )
        else:
            return []
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取运动记录失败: {str(e)}"
        )

@router.post("/", response_model=ExerciseLogResponse, status_code=status.HTTP_201_CREATED)
def create_exercise_log(
    exercise_log: ExerciseLogCreate,
    db: Session = Depends(get_db)
):
    """
    创建运动记录
    
    - **user_id**: 用户ID
    - **exercise_type**: 运动类型
    - **duration_minutes**: 运动时长（分钟）
    - **log_date**: 记录日期
    """
    try:
        return ExerciseLogService.create_exercise_log(db=db, exercise_log=exercise_log)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建运动记录失败: {str(e)}"
        )

@router.get("/user/{user_id}", response_model=List[ExerciseLogResponse])
def get_user_exercise_logs(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取用户的运动记录"""
    try:
        return ExerciseLogService.get_exercise_logs_by_user(
            db=db, user_id=user_id, skip=skip, limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取运动记录失败: {str(e)}"
        )

@router.get("/{log_id}", response_model=ExerciseLogResponse)
def get_exercise_log(
    log_id: int,
    db: Session = Depends(get_db)
):
    """根据ID获取运动记录"""
    exercise_log = ExerciseLogService.get_exercise_log_by_id(db=db, log_id=log_id)
    if not exercise_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="运动记录未找到"
        )
    return exercise_log

@router.delete("/{log_id}")
def delete_exercise_log(
    log_id: int,
    db: Session = Depends(get_db)
):
    """删除运动记录"""
    success = ExerciseLogService.delete_exercise_log(db=db, log_id=log_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="运动记录未找到"
        )
    return {"message": "运动记录已成功删除"} 