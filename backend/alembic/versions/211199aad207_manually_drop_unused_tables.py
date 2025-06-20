"""manually_drop_unused_tables

Revision ID: 211199aad207
Revises: e84868cf6f21
Create Date: 2025-06-14 20:45:09.709998

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '211199aad207'
down_revision = 'e84868cf6f21'
branch_labels = None
depends_on = None


def upgrade():
    # 删除不需要的表
    # 这些表不在当前的模型中，需要手动删除
    
    # 删除身体测量表
    op.drop_table('body_measurements')
    
    # 删除饮食记录表
    op.drop_table('diet_record')
    
    # 删除健康预测表
    op.drop_table('health_predictions')
    
    # 删除健康提醒表
    op.drop_table('health_reminders')
    
    # 删除预测模型表
    op.drop_table('prediction_models')
    
    # 删除用户健康趋势表
    op.drop_table('user_health_trends')


def downgrade():
    # 注意：这里不重新创建表，因为我们不再需要它们
    # 如果需要恢复，可以从之前的迁移中找到表结构
    pass
