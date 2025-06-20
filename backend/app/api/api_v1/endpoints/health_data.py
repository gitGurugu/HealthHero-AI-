from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import logging

from app.schemas.health_data import HealthDataCreate, HealthDataResponse
from app.db.session import get_db
from app.services.health_data import HealthDataService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[HealthDataResponse])
def get_health_data_list(
    skip: int = 0,
    limit: int = 10,
    user_id: int = None,
    db: Session = Depends(get_db)
):
    """
    获取健康数据记录列表
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的记录数限制
    - **user_id**: 可选，指定用户ID
    """
    try:
        logger.info(f"收到健康数据查询请求: user_id={user_id}, skip={skip}, limit={limit}")
        if user_id:
            result = HealthDataService.get_health_data_by_user(
                db=db, user_id=user_id, skip=skip, limit=limit
            )
            logger.info(f"成功返回 {len(result)} 条健康数据记录")
            return result
        else:
            # 如果没有指定用户ID，返回空列表或者需要认证
            logger.info("未指定用户ID，返回空列表")
            return []
    except Exception as e:
        logger.error(f"获取健康数据失败: {str(e)}")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"错误详情: {repr(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取健康数据失败: {str(e)}"
        )

@router.post("/", response_model=HealthDataResponse, status_code=status.HTTP_201_CREATED)
def create_health_data(
    health_data: HealthDataCreate,
    db: Session = Depends(get_db)
):
    """
    创建健康数据记录
    
    - **user_id**: 用户ID
    - **date**: 记录日期
    - **weight**: 体重(kg)，可选
    - **height**: 身高(cm)，可选
    - **blood_pressure_systolic**: 收缩压，可选
    - **blood_pressure_diastolic**: 舒张压，可选
    - **heart_rate**: 心率，可选
    - **temperature**: 体温，可选
    - **notes**: 备注，可选
    """
    try:
        logger.info(f"收到创建健康数据请求: {health_data}")
        result = HealthDataService.create_health_data(db=db, health_data=health_data)
        logger.info(f"成功创建健康数据记录: ID={result.id}")
        return result
    except Exception as e:
        logger.error(f"创建健康数据失败: {str(e)}")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"错误详情: {repr(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建健康数据失败: {str(e)}"
        )

@router.get("/user/{user_id}", response_model=List[HealthDataResponse])
def get_user_health_data(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取指定用户的健康数据记录"""
    try:
        logger.info(f"收到用户健康数据查询请求: user_id={user_id}, skip={skip}, limit={limit}")
        result = HealthDataService.get_health_data_by_user(
            db=db, user_id=user_id, skip=skip, limit=limit
        )
        logger.info(f"成功返回用户 {user_id} 的 {len(result)} 条健康数据记录")
        return result
    except Exception as e:
        logger.error(f"获取用户健康数据失败: {str(e)}")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"错误详情: {repr(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取健康数据失败: {str(e)}"
        )

@router.get("/{health_data_id}", response_model=HealthDataResponse)
def get_health_data(
    health_data_id: int,
    db: Session = Depends(get_db)
):
    """根据ID获取健康数据记录"""
    try:
        logger.info(f"收到健康数据详情查询请求: health_data_id={health_data_id}")
        health_data = HealthDataService.get_health_data_by_id(db=db, health_data_id=health_data_id)
        if not health_data:
            logger.warning(f"健康数据记录未找到: ID={health_data_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="健康数据记录未找到"
            )
        logger.info(f"成功返回健康数据记录: ID={health_data_id}")
        return health_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取健康数据详情失败: {str(e)}")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"错误详情: {repr(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取健康数据失败: {str(e)}"
        )

@router.get("/user/{user_id}/date-range", response_model=List[HealthDataResponse])
def get_health_data_by_date_range(
    user_id: int,
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db)
):
    """根据日期范围获取用户的健康数据记录"""
    try:
        logger.info(f"收到日期范围健康数据查询请求: user_id={user_id}, start_date={start_date}, end_date={end_date}")
        result = HealthDataService.get_health_data_by_date_range(
            db=db, user_id=user_id, start_date=start_date, end_date=end_date
        )
        logger.info(f"成功返回用户 {user_id} 在 {start_date} 到 {end_date} 期间的 {len(result)} 条健康数据记录")
        return result
    except Exception as e:
        logger.error(f"获取日期范围健康数据失败: {str(e)}")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"错误详情: {repr(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取健康数据失败: {str(e)}"
        )

@router.put("/{health_data_id}", response_model=HealthDataResponse)
def update_health_data(
    health_data_id: int,
    health_data_update: HealthDataCreate,
    db: Session = Depends(get_db)
):
    """更新健康数据记录"""
    try:
        logger.info(f"收到更新健康数据请求: health_data_id={health_data_id}")
        health_data = HealthDataService.update_health_data(
            db=db, health_data_id=health_data_id, health_data_update=health_data_update
        )
        if not health_data:
            logger.warning(f"要更新的健康数据记录未找到: ID={health_data_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="健康数据记录未找到"
            )
        logger.info(f"成功更新健康数据记录: ID={health_data_id}")
        return health_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新健康数据失败: {str(e)}")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"错误详情: {repr(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新健康数据失败: {str(e)}"
        )

@router.delete("/{health_data_id}")
def delete_health_data(
    health_data_id: int,
    db: Session = Depends(get_db)
):
    """删除健康数据记录"""
    try:
        logger.info(f"收到删除健康数据请求: health_data_id={health_data_id}")
        success = HealthDataService.delete_health_data(db=db, health_data_id=health_data_id)
        if not success:
            logger.warning(f"要删除的健康数据记录未找到: ID={health_data_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="健康数据记录未找到"
            )
        logger.info(f"成功删除健康数据记录: ID={health_data_id}")
        return {"message": "健康数据记录已成功删除"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除健康数据失败: {str(e)}")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"错误详情: {repr(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除健康数据失败: {str(e)}"
        ) 