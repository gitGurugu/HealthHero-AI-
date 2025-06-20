#!/usr/bin/env python3
"""
为特定用户生成随机健康数据的脚本
"""

import sys
import os
import random
from datetime import datetime, timedelta
from typing import Optional

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.models.user import User
from app.models.health_data import HealthData


def generate_realistic_health_data(base_weight: float = 70.0, base_height: float = 170.0) -> dict:
    """
    生成符合现实范围的健康数据，严格按照数据库约束
    """
    # 体重：30-300kg，变化范围 ±5kg
    weight = round(random.uniform(max(30, base_weight - 5), min(300, base_weight + 5)), 1)
    
    # 身高：必须>0，基本不变，偶尔有小幅变化（测量误差）
    height = round(random.uniform(max(1, base_height - 2), base_height + 2), 2)
    
    # 收缩压：50-250
    systolic = random.randint(110, 140)
    
    # 舒张压：30-150
    diastolic = random.randint(70, 90)
    
    # 血糖：无约束，但合理范围
    blood_sugar = round(random.uniform(4.5, 7.0), 1)
    
    # 胆固醇：>=0
    cholesterol = round(random.uniform(3.5, 6.5), 1)
    
    return {
        'weight': weight,
        'height': height,
        'systolic_pressure': systolic,
        'diastolic_pressure': diastolic,
        'blood_sugar': blood_sugar,
        'cholesterol': cholesterol
    }


def insert_health_data_for_user(user_id: int, count: int, days_back: int = 30):
    """
    为指定用户插入健康数据
    
    Args:
        user_id: 用户ID
        count: 要插入的数据条数
        days_back: 数据分布的天数范围（从今天往前推）
    """
    db = SessionLocal()
    
    try:
        # 检查用户是否存在
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"错误: 用户ID {user_id} 不存在")
            return False
        
        print(f"为用户 {user.username} (ID: {user_id}) 生成 {count} 条健康数据...")
        
        # 获取用户现有的健康数据作为基准
        existing_data = db.query(HealthData).filter(
            HealthData.user_id == user_id
        ).order_by(HealthData.record_date.desc()).first()
        
        # 设置基准值
        base_weight = 70.0
        base_height = 170.0
        
        if existing_data:
            if existing_data.weight:
                base_weight = float(existing_data.weight)
            if existing_data.height:
                base_height = float(existing_data.height)
            print(f"基于现有数据设置基准: 体重={base_weight}kg, 身高={base_height}cm")
        else:
            print(f"使用默认基准值: 体重={base_weight}kg, 身高={base_height}cm")
        
        # 生成时间序列
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # 生成随机日期
        dates = []
        for i in range(count):
            random_days = random.randint(0, days_back)
            record_date = end_date - timedelta(days=random_days)
            dates.append(record_date)
        
        # 按日期排序
        dates.sort()
        
        # 插入数据
        inserted_count = 0
        for i, record_date in enumerate(dates):
            # 生成健康数据
            health_data = generate_realistic_health_data(base_weight, base_height)
            
            # 创建健康记录
            health_record = HealthData(
                user_id=user_id,
                record_date=record_date,
                weight=health_data['weight'],
                height=health_data['height'],
                systolic_pressure=health_data['systolic_pressure'],
                diastolic_pressure=health_data['diastolic_pressure'],
                blood_sugar=health_data['blood_sugar'],
                cholesterol=health_data['cholesterol']
            )
            
            db.add(health_record)
            inserted_count += 1
            
            # 每10条提交一次
            if inserted_count % 10 == 0:
                db.commit()
                print(f"已插入 {inserted_count}/{count} 条数据...")
        
        # 最终提交
        db.commit()
        print(f"✅ 成功为用户 {user.username} 插入了 {inserted_count} 条健康数据")
        print(f"数据时间范围: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ 插入数据时发生错误: {str(e)}")
        return False
    finally:
        db.close()


def main():
    """
    主函数 - 处理命令行参数
    """
    if len(sys.argv) < 3:
        print("使用方法: python generate_user_health_data.py <用户ID> <数据条数> [天数范围]")
        print("示例: python generate_user_health_data.py 6 50 30")
        print("      为用户ID=6生成50条数据，分布在最近30天内")
        return
    
    try:
        user_id = int(sys.argv[1])
        count = int(sys.argv[2])
        days_back = int(sys.argv[3]) if len(sys.argv) > 3 else 30
        
        if count <= 0:
            print("错误: 数据条数必须大于0")
            return
        
        if days_back <= 0:
            print("错误: 天数范围必须大于0")
            return
        
        print(f"准备为用户ID {user_id} 生成 {count} 条健康数据，分布在最近 {days_back} 天内")
        
        # 确认操作
        confirm = input("确认执行吗？(y/N): ").strip().lower()
        if confirm not in ['y', 'yes', '是']:
            print("操作已取消")
            return
        
        # 执行插入
        success = insert_health_data_for_user(user_id, count, days_back)
        
        if success:
            print("\n🎉 数据生成完成！现在可以查看数据大屏的趋势图了。")
        else:
            print("\n❌ 数据生成失败，请检查错误信息。")
            
    except ValueError:
        print("错误: 用户ID和数据条数必须是数字")
    except Exception as e:
        print(f"错误: {str(e)}")


if __name__ == "__main__":
    main() 