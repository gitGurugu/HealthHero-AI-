from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.symptom_records import SymptomRecordsCreate, SymptomRecordsResponse
from app.db.session import get_db
from app.services.symptom_records import SymptomRecordsService

router = APIRouter()

@router.post("/", response_model=SymptomRecordsResponse, status_code=status.HTTP_201_CREATED)
def create_symptom_record(
    symptom_record: SymptomRecordsCreate,
    db: Session = Depends(get_db)
):
    """
    创建症状记录
    
    - **user_id**: 用户ID
    - **record_date**: 记录日期
    - **symptom_type**: 症状类型
    - **severity**: 严重程度评分(1-10)
    - **description**: 症状描述
    - **duration_hours**: 持续时间(小时)
    - **location**: 症状位置
    - **triggers**: 触发因素
    """
    try:
        return SymptomRecordsService.create_symptom_record(db=db, symptom_record=symptom_record)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建症状记录失败: {str(e)}"
        )

@router.get("/user/{user_id}", response_model=List[SymptomRecordsResponse])
def get_user_symptom_records(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取用户的症状记录"""
    try:
        return SymptomRecordsService.get_symptom_records_by_user(
            db=db, user_id=user_id, skip=skip, limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取症状记录失败: {str(e)}"
        )

@router.get("/{symptom_id}", response_model=SymptomRecordsResponse)
def get_symptom_record(
    symptom_id: int,
    db: Session = Depends(get_db)
):
    """根据ID获取症状记录"""
    symptom_record = SymptomRecordsService.get_symptom_record_by_id(db=db, symptom_id=symptom_id)
    if not symptom_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="症状记录未找到"
        )
    return symptom_record

@router.delete("/{symptom_id}")
def delete_symptom_record(
    symptom_id: int,
    db: Session = Depends(get_db)
):
    """删除症状记录"""
    success = SymptomRecordsService.delete_symptom_record(db=db, symptom_id=symptom_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="症状记录未找到"
        )
    return {"message": "症状记录已成功删除"} 