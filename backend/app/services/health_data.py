from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from typing import List, Optional
import logging

from app.models.health_data import HealthData
from app.schemas.health_data import HealthDataCreate

logger = logging.getLogger(__name__)

class HealthDataService:
    
    @staticmethod
    def create_health_data(db: Session, health_data: HealthDataCreate) -> HealthData:
        """
        创建新的健康数据记录
        """
        try:
            db_health_data = HealthData(
                user_id=health_data.user_id,
                record_date=health_data.record_date,
                height=health_data.height,
                weight=health_data.weight,
                systolic_pressure=health_data.systolic_pressure,
                diastolic_pressure=health_data.diastolic_pressure,
                blood_sugar=health_data.blood_sugar,
                cholesterol=health_data.cholesterol,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(db_health_data)
            db.commit()
            db.refresh(db_health_data)
            return db_health_data
        except SQLAlchemyError as e:
            logger.error(f"创建健康数据时数据库错误: {str(e)}")
            db.rollback()
            raise e
        except Exception as e:
            logger.error(f"创建健康数据时未知错误: {str(e)}")
            logger.error(f"错误类型: {type(e).__name__}")
            db.rollback()
            raise e
    
    @staticmethod
    def get_health_data_by_user(
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[HealthData]:
        """
        获取用户的健康数据记录
        """
        try:
            logger.info(f"查询用户 {user_id} 的健康数据，skip={skip}, limit={limit}")
            result = db.query(HealthData).filter(
                HealthData.user_id == user_id
            ).order_by(HealthData.record_date.desc()).offset(skip).limit(limit).all()
            logger.info(f"查询到 {len(result)} 条健康数据记录")
            return result
        except SQLAlchemyError as e:
            logger.error(f"查询健康数据时数据库错误: {str(e)}")
            logger.error(f"查询参数: user_id={user_id}, skip={skip}, limit={limit}")
            db.rollback()
            raise e
        except Exception as e:
            logger.error(f"查询健康数据时未知错误: {str(e)}")
            logger.error(f"错误类型: {type(e).__name__}")
            logger.error(f"查询参数: user_id={user_id}, skip={skip}, limit={limit}")
            db.rollback()
            raise e
    
    @staticmethod
    def get_health_data_by_id(db: Session, health_data_id: int) -> Optional[HealthData]:
        """
        根据ID获取健康数据记录
        """
        try:
            return db.query(HealthData).filter(HealthData.record_id == health_data_id).first()
        except SQLAlchemyError as e:
            logger.error(f"根据ID查询健康数据时数据库错误: {str(e)}")
            db.rollback()
            raise e
        except Exception as e:
            logger.error(f"根据ID查询健康数据时未知错误: {str(e)}")
            logger.error(f"错误类型: {type(e).__name__}")
            db.rollback()
            raise e
    
    @staticmethod
    def get_health_data_by_date_range(
        db: Session,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[HealthData]:
        """
        根据日期范围获取健康数据记录
        """
        try:
            return db.query(HealthData).filter(
                HealthData.user_id == user_id,
                HealthData.record_date >= start_date,
                HealthData.record_date <= end_date
            ).order_by(HealthData.record_date.desc()).all()
        except SQLAlchemyError as e:
            logger.error(f"根据日期范围查询健康数据时数据库错误: {str(e)}")
            db.rollback()
            raise e
        except Exception as e:
            logger.error(f"根据日期范围查询健康数据时未知错误: {str(e)}")
            logger.error(f"错误类型: {type(e).__name__}")
            db.rollback()
            raise e
    
    @staticmethod
    def update_health_data(
        db: Session, 
        health_data_id: int, 
        health_data_update: HealthDataCreate
    ) -> Optional[HealthData]:
        """
        更新健康数据记录
        """
        try:
            db_health_data = db.query(HealthData).filter(HealthData.record_id == health_data_id).first()
            if db_health_data:
                for field, value in health_data_update.dict(exclude_unset=True).items():
                    setattr(db_health_data, field, value)
                db_health_data.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(db_health_data)
            return db_health_data
        except SQLAlchemyError as e:
            logger.error(f"更新健康数据时数据库错误: {str(e)}")
            db.rollback()
            raise e
        except Exception as e:
            logger.error(f"更新健康数据时未知错误: {str(e)}")
            logger.error(f"错误类型: {type(e).__name__}")
            db.rollback()
            raise e
    
    @staticmethod
    def delete_health_data(db: Session, health_data_id: int) -> bool:
        """
        删除健康数据记录
        """
        try:
            db_health_data = db.query(HealthData).filter(HealthData.record_id == health_data_id).first()
            if db_health_data:
                db.delete(db_health_data)
                db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            logger.error(f"删除健康数据时数据库错误: {str(e)}")
            db.rollback()
            raise e
        except Exception as e:
            logger.error(f"删除健康数据时未知错误: {str(e)}")
            logger.error(f"错误类型: {type(e).__name__}")
            db.rollback()
            raise e 