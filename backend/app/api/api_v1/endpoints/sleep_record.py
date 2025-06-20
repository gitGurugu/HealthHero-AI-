from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.sleep_record import SleepRecordCreate, SleepRecordResponse
from app.db.session import get_db
from app.services.sleep_record import SleepRecordService

router = APIRouter()

@router.get("/", response_model=List[SleepRecordResponse])
def get_sleep_records_list(
    skip: int = 0,
    limit: int = 10,
    user_id: int = None,
    db: Session = Depends(get_db)
):
    """
    获取睡眠记录列表
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的记录数限制
    - **user_id**: 可选，指定用户ID
    """
    try:
        if user_id:
            return SleepRecordService.get_sleep_records_by_user(
                db=db, user_id=user_id, skip=skip, limit=limit
            )
        else:
            return []
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取睡眠记录失败: {str(e)}"
        )

@router.post("/", response_model=SleepRecordResponse, status_code=status.HTTP_201_CREATED)
def create_sleep_record(
    sleep_record: SleepRecordCreate,
    db: Session = Depends(get_db)
):
    """
    创建睡眠记录
    
    - **user_id**: 用户ID
    - **sleep_date**: 睡眠日期
    - **bedtime**: 就寝时间
    - **wake_time**: 起床时间
    - **sleep_duration**: 睡眠时长
    - **sleep_quality**: 睡眠质量评分(1-10)
    - **deep_sleep_hours**: 深度睡眠时长
    - **notes**: 备注
    """
    try:
        return SleepRecordService.create_sleep_record(db=db, sleep_record=sleep_record)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建睡眠记录失败: {str(e)}"
        )

@router.get("/user/{user_id}", response_model=List[SleepRecordResponse])
def get_user_sleep_records(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取用户的睡眠记录"""
    try:
        return SleepRecordService.get_sleep_records_by_user(
            db=db, user_id=user_id, skip=skip, limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取睡眠记录失败: {str(e)}"
        )

@router.get("/{sleep_id}", response_model=SleepRecordResponse)
def get_sleep_record(
    sleep_id: int,
    db: Session = Depends(get_db)
):
    """根据ID获取睡眠记录"""
    sleep_record = SleepRecordService.get_sleep_record_by_id(db=db, sleep_id=sleep_id)
    if not sleep_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="睡眠记录未找到"
        )
    return sleep_record

@router.delete("/{sleep_id}")
def delete_sleep_record(
    sleep_id: int,
    db: Session = Depends(get_db)
):
    """删除睡眠记录"""
    success = SleepRecordService.delete_sleep_record(db=db, sleep_id=sleep_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="睡眠记录未找到"
        )
    return {"message": "睡眠记录已成功删除"} 